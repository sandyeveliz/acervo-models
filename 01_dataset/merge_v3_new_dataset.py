#!/usr/bin/env python3
"""
Merge v3-new training dataset from all cleaned + new sources.

Combines:
  - training_data/v3_new/v2_cleaned_training.jsonl (891 cleaned v2 examples)
  - training_data/v3_new/v2_cleaned_validation.jsonl (83 cleaned v2 validation)
  - training_data/v3_new/v3_g1_cleaned.jsonl ... v3_g4_cleaned.jsonl (185 cleaned v3 groups)
  - training_data/v3_new/v3_new_g5_*.jsonl ... v3_new_g10_*.jsonl (540 new examples)
Into:
  - training_data/v3_new/s1_v3_new_full_training.jsonl
  - training_data/v3_new/s1_v3_new_full_validation.jsonl

Usage:
    cd 01_dataset
    python merge_v3_new_dataset.py
"""

import json
import hashlib
import random
from pathlib import Path
from collections import Counter

from schema import validate_s1

PROJECT_ROOT = Path(__file__).resolve().parent.parent
V3_NEW_DIR = PROJECT_ROOT / "training_data" / "v3_new"

# Cleaned existing data
V2_CLEANED_TRAIN = V3_NEW_DIR / "v2_cleaned_training.jsonl"
V2_CLEANED_VAL = V3_NEW_DIR / "v2_cleaned_validation.jsonl"
V3_CLEANED_FILES = [
    V3_NEW_DIR / "v3_g1_cleaned.jsonl",
    V3_NEW_DIR / "v3_g2_cleaned.jsonl",
    V3_NEW_DIR / "v3_g3_cleaned.jsonl",
    V3_NEW_DIR / "v3_g4_cleaned.jsonl",
]

# New generated data
V3_NEW_FILES = [
    V3_NEW_DIR / "v3_new_g5_facts_personal.jsonl",
    V3_NEW_DIR / "v3_new_g6_entities_relations.jsonl",
    V3_NEW_DIR / "v3_new_g7_facts_existing.jsonl",
    V3_NEW_DIR / "v3_new_g8_missing_relations.jsonl",
    V3_NEW_DIR / "v3_new_g9_intent_personal.jsonl",
    V3_NEW_DIR / "v3_new_g10_edge_cases.jsonl",
]

# Output
TRAIN_OUTPUT = V3_NEW_DIR / "s1_v3_new_full_training.jsonl"
VAL_OUTPUT = V3_NEW_DIR / "s1_v3_new_full_validation.jsonl"

VAL_SPLIT = 0.10


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


def main():
    random.seed(42)

    print("=" * 60)
    print("Merging v3-new training dataset")
    print("=" * 60)

    # ── Load cleaned v2 ──
    print("\n--- Cleaned v2 base ---")
    v2_train = load_jsonl(V2_CLEANED_TRAIN)
    print(f"  v2 training: {len(v2_train)}")
    v2_val = load_jsonl(V2_CLEANED_VAL)
    print(f"  v2 validation: {len(v2_val)}")

    # ── Load cleaned v3 groups ──
    print("\n--- Cleaned v3 groups ---")
    v3_cleaned = []
    for path in V3_CLEANED_FILES:
        if not path.exists():
            print(f"  SKIP: {path.name}")
            continue
        examples = load_jsonl(path)
        print(f"  {path.name}: {len(examples)}")
        v3_cleaned.extend(examples)

    # ── Load new v3 data ──
    print("\n--- New v3 data ---")
    v3_new = []
    for path in V3_NEW_FILES:
        if not path.exists():
            print(f"  SKIP: {path.name}")
            continue
        examples = load_jsonl(path)
        print(f"  {path.name}: {len(examples)}")
        v3_new.extend(examples)

    # ── Validate all ──
    print(f"\nValidating all examples...")
    all_sources = [
        ("v2_train", v2_train), ("v2_val", v2_val),
        ("v3_cleaned", v3_cleaned), ("v3_new", v3_new),
    ]
    for name, examples in all_sources:
        valid = 0
        invalid = 0
        for ex in examples:
            ok, result = validate_s1(ex["messages"][2]["content"])
            if ok:
                valid += 1
            else:
                invalid += 1
                if invalid <= 2:
                    print(f"  {name} INVALID: {result}")
        print(f"  {name}: {valid} valid, {invalid} invalid")

    # ── Split new data into train/val ──
    all_new = v3_cleaned + v3_new
    random.shuffle(all_new)
    val_count = max(1, int(len(all_new) * VAL_SPLIT))
    new_val = all_new[:val_count]
    new_train = all_new[val_count:]
    print(f"\n  New data split: {len(new_train)} train, {len(new_val)} val")

    # ── Combine ──
    all_train = v2_train + new_train
    all_val = v2_val + new_val

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
    print("\n" + "=" * 60)
    print("FINAL DATASET STATISTICS")
    print("=" * 60)
    all_examples = train_deduped + val_deduped
    total = len(all_examples)

    intents = Counter()
    retrievals = Counter()
    topics = Counter()
    entity_types = Counter()
    relation_types = Counter()
    has_entities = 0
    has_relations = 0
    has_facts = 0
    total_entities = 0
    total_relations = 0
    total_facts = 0
    spanish = 0

    for ex in all_examples:
        output = json.loads(ex["messages"][2]["content"])
        intents[output["intent"]] += 1
        retrievals[output["retrieval"]] += 1
        topics[output["topic"]["action"]] += 1

        ents = output.get("entities", [])
        rels = output.get("relations", [])
        facts = output.get("facts", [])

        if ents:
            has_entities += 1
        if rels:
            has_relations += 1
        if facts:
            has_facts += 1

        total_entities += len(ents)
        total_relations += len(rels)
        total_facts += len(facts)

        for e in ents:
            entity_types[e.get("type", "?")] += 1
        for r in rels:
            relation_types[r.get("relation", "?")] += 1

        # Also count facts attached to new entities
        for e in ents:
            for f in e.get("facts", []):
                total_facts += 1
                if not facts and not has_facts:
                    has_facts += 1

        # Language detection
        user_msg = ex["messages"][1]["content"]
        if any(w in user_msg.lower() for w in ["qué", "cómo", "podés", "está", "también",
                                                  "tengo", "fuimos", "hicimos", "barrio"]):
            spanish += 1

    print(f"\nTotal: {total} (train: {len(train_deduped)}, val: {len(val_deduped)})")

    print(f"\nLanguage (approx): Spanish={spanish} ({spanish*100/total:.0f}%), English={total-spanish} ({(total-spanish)*100/total:.0f}%)")

    print(f"\nIntent distribution:")
    for intent, count in sorted(intents.items(), key=lambda x: -x[1]):
        pct = count / total * 100
        bar = "#" * int(pct / 2)
        print(f"  {intent:12s}: {count:4d} ({pct:5.1f}%) {bar}")

    print(f"\nRetrieval distribution:")
    for ret, count in sorted(retrievals.items(), key=lambda x: -x[1]):
        pct = count / total * 100
        print(f"  {ret:14s}: {count:4d} ({pct:5.1f}%)")

    print(f"\nExtraction content:")
    print(f"  With entities:  {has_entities:4d} ({has_entities*100/total:.1f}%)")
    print(f"  With relations: {has_relations:4d} ({has_relations*100/total:.1f}%)")
    print(f"  With facts:     {has_facts:4d} ({has_facts*100/total:.1f}%)")
    print(f"  Avg entities/ex: {total_entities/total:.2f}")
    print(f"  Avg relations/ex: {total_relations/total:.2f}")
    print(f"  Avg facts/ex: {total_facts/total:.2f}")

    print(f"\nEntity types:")
    for etype, count in sorted(entity_types.items(), key=lambda x: -x[1]):
        print(f"  {etype:15s}: {count:4d}")

    print(f"\nRelation types:")
    for rtype, count in sorted(relation_types.items(), key=lambda x: -x[1]):
        print(f"  {rtype:18s}: {count:4d}")

    # ── Quality checks ──
    print("\n--- Quality Checks ---")
    all_ok = True
    for intent, count in intents.items():
        pct = count / total * 100
        if pct > 55:
            print(f"  WARNING: {intent} is {pct:.1f}% (>55%)")
            all_ok = False
        if pct < 3:
            print(f"  WARNING: {intent} is {pct:.1f}% (<3%)")
            all_ok = False

    if has_facts / total < 0.25:
        print(f"  WARNING: fact coverage is {has_facts*100/total:.1f}% (<25%)")
        all_ok = False

    parse_ok = sum(1 for ex in all_examples
                   if json.loads(ex["messages"][2]["content"]))
    print(f"  JSON parse rate: {parse_ok/total*100:.1f}%")

    if all_ok:
        print("\n  All quality checks PASSED")
    else:
        print("\n  Some checks FAILED -- review warnings")


if __name__ == "__main__":
    main()
