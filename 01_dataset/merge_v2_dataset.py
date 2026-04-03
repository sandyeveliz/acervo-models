#!/usr/bin/env python3
"""
Merge v1-migrated and v2-new training data into final dataset.

Combines:
  - training_data/v2/s1_extraction.jsonl (v1 migrated)
  - training_data/v2/s1_suplementary_training.jsonl (v1 migrated)
  - training_data/v2/s1_stress_test.jsonl (v1 migrated)
  - training_data/v2/s1_v2_new_training.jsonl (v2 new)
Into:
  - training_data/v2/s1_v2_full_training.jsonl

And:
  - training_data/v2/s1_validation.jsonl (v1 migrated)
  - training_data/v2/s1_v2_new_validation.jsonl (v2 new)
Into:
  - training_data/v2/s1_v2_full_validation.jsonl

Also adds benchmark_failures.jsonl to training set.

Usage:
    python 01_dataset/merge_v2_dataset.py
"""

import json
import hashlib
import random
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "training_data" / "v2"
FAILURES_PATH = PROJECT_ROOT / "01_dataset" / "benchmark_failures.jsonl"

TRAIN_INPUTS = [
    DATA_DIR / "s1_extraction.jsonl",
    DATA_DIR / "s1_suplementary_training.jsonl",
    DATA_DIR / "s1_stress_test.jsonl",
    DATA_DIR / "s1_v2_new_training.jsonl",
    FAILURES_PATH,
]

VAL_INPUTS = [
    DATA_DIR / "s1_validation.jsonl",
    DATA_DIR / "s1_v2_new_validation.jsonl",
]

TRAIN_OUTPUT = DATA_DIR / "s1_v2_full_training.jsonl"
VAL_OUTPUT = DATA_DIR / "s1_v2_full_validation.jsonl"


def example_hash(example: dict) -> str:
    """Hash user message + assistant output for dedup."""
    user = example["messages"][1]["content"]
    assistant = example["messages"][2]["content"]
    return hashlib.md5((user + assistant).encode()).hexdigest()


def load_jsonl(path: Path) -> list[dict]:
    """Load examples from a JSONL file."""
    examples = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                examples.append(json.loads(line))
    return examples


def validate_v2_schema(example: dict) -> tuple[bool, str]:
    """Check that an example has v2 fields."""
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
    print("Merging v2 training dataset")
    print("=" * 60)

    # ── Load and merge training data ──
    train_examples = []
    for path in TRAIN_INPUTS:
        if not path.exists():
            print(f"  SKIP: {path} (not found)")
            continue
        examples = load_jsonl(path)
        print(f"  {path.name}: {len(examples)} examples")
        train_examples.extend(examples)

    # ── Load and merge validation data ──
    val_examples = []
    for path in VAL_INPUTS:
        if not path.exists():
            print(f"  SKIP: {path} (not found)")
            continue
        examples = load_jsonl(path)
        print(f"  {path.name}: {len(examples)} examples")
        val_examples.extend(examples)

    # ── Validate schema ──
    print(f"\nValidating v2 schema...")
    train_valid = []
    train_invalid = 0
    for ex in train_examples:
        ok, err = validate_v2_schema(ex)
        if ok:
            train_valid.append(ex)
        else:
            train_invalid += 1
            if train_invalid <= 5:
                user_msg = ex["messages"][1]["content"][-80:]
                print(f"  INVALID: {err} — ...{user_msg}")

    val_valid = []
    val_invalid = 0
    for ex in val_examples:
        ok, err = validate_v2_schema(ex)
        if ok:
            val_valid.append(ex)
        else:
            val_invalid += 1

    print(f"  Training: {len(train_valid)} valid, {train_invalid} invalid")
    print(f"  Validation: {len(val_valid)} valid, {val_invalid} invalid")

    # ── Dedup ──
    seen = set()
    train_deduped = []
    dupes = 0
    for ex in train_valid:
        h = example_hash(ex)
        if h not in seen:
            seen.add(h)
            train_deduped.append(ex)
        else:
            dupes += 1

    val_deduped = []
    for ex in val_valid:
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
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    with open(TRAIN_OUTPUT, "w", encoding="utf-8") as f:
        for ex in train_deduped:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    print(f"\nWrote {len(train_deduped)} training examples to {TRAIN_OUTPUT}")

    with open(VAL_OUTPUT, "w", encoding="utf-8") as f:
        for ex in val_deduped:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    print(f"Wrote {len(val_deduped)} validation examples to {VAL_OUTPUT}")

    # ── Stats ──
    print("\n--- Final Dataset Stats ---")
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

    print(f"\nTotal: {total} examples (train: {len(train_deduped)}, val: {len(val_deduped)})")
    print(f"\nIntent distribution:")
    for intent, count in sorted(intents.items()):
        pct = count / total * 100
        bar = "#" * int(pct / 2)
        print(f"  {intent:12s}: {count:4d} ({pct:5.1f}%) {bar}")

    print(f"\nRetrieval distribution:")
    for ret, count in sorted(retrievals.items()):
        pct = count / total * 100
        print(f"  {ret:14s}: {count:4d} ({pct:5.1f}%)")

    print(f"\nTopic action distribution:")
    for action, count in sorted(topics.items()):
        pct = count / total * 100
        print(f"  {action:10s}: {count:4d} ({pct:5.1f}%)")

    avg_entities = sum(entity_counts) / len(entity_counts) if entity_counts else 0
    empty = sum(1 for c in entity_counts if c == 0)
    print(f"\nEntity stats: avg={avg_entities:.1f}, empty={empty} ({empty/total*100:.1f}%)")

    # ── Quality checks ──
    print("\n--- Quality Checks ---")
    checks_passed = True

    # No intent > 40% or < 5%
    for intent, count in intents.items():
        pct = count / total * 100
        if pct > 45:
            print(f"  WARNING: {intent} is {pct:.1f}% (>45%)")
            checks_passed = False
        if pct < 5:
            print(f"  WARNING: {intent} is {pct:.1f}% (<5%)")
            checks_passed = False

    # JSON parse rate
    parse_ok = 0
    for ex in all_examples:
        try:
            json.loads(ex["messages"][2]["content"])
            parse_ok += 1
        except json.JSONDecodeError:
            pass
    parse_rate = parse_ok / total * 100
    print(f"  JSON parse rate: {parse_rate:.1f}%")
    if parse_rate < 100:
        checks_passed = False

    if checks_passed:
        print("\n  All quality checks PASSED")
    else:
        print("\n  Some checks FAILED — review above warnings")


if __name__ == "__main__":
    main()
