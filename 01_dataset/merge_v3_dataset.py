#!/usr/bin/env python3
"""
Merge v2 full dataset + v3 new training data into v3 final dataset.

Combines:
  - training_data/v2/s1_v2_full_training.jsonl (891 v2 examples)
  - training_data/v3/v3_g1_s1_intent.jsonl
  - training_data/v3/v3_g2_s15_recall.jsonl
  - training_data/v3/v3_g3_curate_multientity.jsonl
  - training_data/v3/v3_g4_gaps.jsonl
Into:
  - training_data/v3/s1_v3_full_training.jsonl
  - training_data/v3/s1_v3_full_validation.jsonl

Usage:
    cd 01_dataset
    python merge_v3_dataset.py
"""

import json
import hashlib
import random
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path(__file__).resolve().parent.parent
V2_DIR = PROJECT_ROOT / "training_data" / "v2"
V3_DIR = PROJECT_ROOT / "training_data" / "v3"

# Existing v2 full dataset (already merged and validated)
V2_TRAIN = V2_DIR / "s1_v2_full_training.jsonl"
V2_VAL = V2_DIR / "s1_v2_full_validation.jsonl"

# New v3 files
V3_FILES = [
    V3_DIR / "v3_g1_s1_intent.jsonl",
    V3_DIR / "v3_g2_s15_recall.jsonl",
    V3_DIR / "v3_g3_curate_multientity.jsonl",
    V3_DIR / "v3_g4_gaps.jsonl",
]

# Output
TRAIN_OUTPUT = V3_DIR / "s1_v3_full_training.jsonl"
VAL_OUTPUT = V3_DIR / "s1_v3_full_validation.jsonl"

VAL_SPLIT = 0.10  # 10% of v3 new data goes to validation


def example_hash(example: dict) -> str:
    user = example["messages"][1]["content"]
    assistant = example["messages"][2]["content"]
    return hashlib.md5((user + assistant).encode()).hexdigest()


def load_jsonl(path: Path) -> list[dict]:
    examples = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                examples.append(json.loads(line))
    return examples


def validate_v2_schema(example: dict) -> tuple[bool, str]:
    try:
        output = json.loads(example["messages"][2]["content"])
        if "intent" not in output:
            return False, "missing intent"
        if "retrieval" not in output:
            return False, "missing retrieval"
        if output["intent"] not in ("overview", "specific", "chat", "followup"):
            return False, f"invalid intent: {output['intent']}"
        if output["retrieval"] not in ("summary_only", "with_chunks"):
            return False, f"invalid retrieval: {output['retrieval']}"
        return True, "ok"
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        return False, str(e)


def main():
    random.seed(42)

    print("=" * 60)
    print("Merging v3 training dataset")
    print("=" * 60)

    # ── Load v2 full dataset ──
    print("\n--- v2 base ---")
    v2_train = load_jsonl(V2_TRAIN)
    print(f"  v2 training: {len(v2_train)} examples")
    v2_val = load_jsonl(V2_VAL)
    print(f"  v2 validation: {len(v2_val)} examples")

    # ── Load v3 new data ──
    print("\n--- v3 new ---")
    v3_all = []
    for path in V3_FILES:
        if not path.exists():
            print(f"  SKIP: {path.name} (not found)")
            continue
        examples = load_jsonl(path)
        print(f"  {path.name}: {len(examples)} examples")
        v3_all.extend(examples)

    # ── Validate v3 schema ──
    print(f"\nValidating v3 schema...")
    v3_valid = []
    v3_invalid = 0
    for ex in v3_all:
        ok, err = validate_v2_schema(ex)
        if ok:
            v3_valid.append(ex)
        else:
            v3_invalid += 1
            if v3_invalid <= 5:
                print(f"  INVALID: {err}")
    print(f"  v3: {len(v3_valid)} valid, {v3_invalid} invalid")

    # ── Split v3 into train/val ──
    random.shuffle(v3_valid)
    val_count = max(1, int(len(v3_valid) * VAL_SPLIT))
    v3_val = v3_valid[:val_count]
    v3_train = v3_valid[val_count:]
    print(f"  v3 split: {len(v3_train)} train, {len(v3_val)} val")

    # ── Combine ──
    all_train = v2_train + v3_train
    all_val = v2_val + v3_val

    # ── Dedup ──
    seen = set()
    train_deduped = []
    dupes = 0
    for ex in all_train:
        h = example_hash(ex)
        if h not in seen:
            seen.add(h)
            train_deduped.append(ex)
        else:
            dupes += 1

    val_deduped = []
    for ex in all_val:
        h = example_hash(ex)
        if h not in seen:
            seen.add(h)
            val_deduped.append(ex)
        else:
            dupes += 1

    if dupes:
        print(f"  Removed {dupes} duplicates")

    # ── Shuffle ──
    random.shuffle(train_deduped)
    random.shuffle(val_deduped)

    # ── Write ──
    with open(TRAIN_OUTPUT, "w", encoding="utf-8") as f:
        for ex in train_deduped:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    print(f"\nWrote {len(train_deduped)} training examples to {TRAIN_OUTPUT.name}")

    with open(VAL_OUTPUT, "w", encoding="utf-8") as f:
        for ex in val_deduped:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    print(f"Wrote {len(val_deduped)} validation examples to {VAL_OUTPUT.name}")

    # ── Stats ──
    print("\n--- Final v3 Dataset Stats ---")
    all_examples = train_deduped + val_deduped
    total = len(all_examples)

    intents = Counter()
    retrievals = Counter()
    topics = Counter()
    entity_counts = []
    for ex in all_examples:
        output = json.loads(ex["messages"][2]["content"])
        intents[output["intent"]] += 1
        retrievals[output["retrieval"]] += 1
        topics[output["topic"]["action"]] += 1
        entity_counts.append(len(output.get("entities", [])))

    print(f"\nTotal: {total} (train: {len(train_deduped)}, val: {len(val_deduped)})")
    print(f"\nIntent distribution:")
    for intent, count in sorted(intents.items()):
        pct = count / total * 100
        bar = "#" * int(pct / 2)
        print(f"  {intent:12s}: {count:4d} ({pct:5.1f}%) {bar}")

    print(f"\nRetrieval distribution:")
    for ret, count in sorted(retrievals.items()):
        pct = count / total * 100
        print(f"  {ret:14s}: {count:4d} ({pct:5.1f}%)")

    avg_entities = sum(entity_counts) / len(entity_counts) if entity_counts else 0
    empty = sum(1 for c in entity_counts if c == 0)
    print(f"\nEntity stats: avg={avg_entities:.1f}, empty={empty} ({empty/total*100:.1f}%)")

    # ── Quality checks ──
    print("\n--- Quality Checks ---")
    checks_passed = True
    for intent, count in intents.items():
        pct = count / total * 100
        if pct > 55:
            print(f"  WARNING: {intent} is {pct:.1f}% (>55%)")
            checks_passed = False
        if pct < 5:
            print(f"  WARNING: {intent} is {pct:.1f}% (<5%)")
            checks_passed = False

    parse_ok = sum(1 for ex in all_examples
                   if json.loads(ex["messages"][2]["content"]))
    print(f"  JSON parse rate: {parse_ok / total * 100:.1f}%")

    if checks_passed:
        print("\n  All quality checks PASSED")
    else:
        print("\n  Some checks FAILED — review warnings")


if __name__ == "__main__":
    main()
