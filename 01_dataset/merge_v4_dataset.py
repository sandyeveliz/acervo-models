#!/usr/bin/env python3
"""
Merge V4 training dataset from generated skill groups.

No legacy data — all examples use the V4 schema (nested intent,
entity_id in facts, description on entities).

Input:  training_data/v4/v4_g*.jsonl  (per-skill JSONL files)
Output: training_data/v4/s1_v4_full_training.jsonl
        training_data/v4/s1_v4_full_validation.jsonl

Usage:
    cd 01_dataset
    python merge_v4_dataset.py
"""

import json
import hashlib
import random
from pathlib import Path
from collections import Counter

from schema_v4 import validate_s1_v4, validate_cross_references, RelationType

PROJECT_ROOT = Path(__file__).resolve().parent.parent
V4_DIR = PROJECT_ROOT / "training_data" / "v4"

TRAIN_OUTPUT = V4_DIR / "s1_v4_full_training.jsonl"
VAL_OUTPUT = V4_DIR / "s1_v4_full_validation.jsonl"

VAL_SPLIT = 0.10


def example_hash(ex: dict) -> str:
    user = ex["messages"][1]["content"]
    assistant = ex["messages"][2]["content"]
    return hashlib.md5((user + assistant).encode()).hexdigest()


def load_jsonl(path: Path) -> list[dict]:
    examples = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                examples.append(json.loads(line))
    return examples


def parse_existing_nodes(user_content: str) -> list[dict]:
    prefix = "EXISTING NODES:\n"
    if prefix not in user_content:
        return []
    start = user_content.index(prefix) + len(prefix)
    end = user_content.find("\n\n", start)
    if end == -1:
        end = len(user_content)
    try:
        return json.loads(user_content[start:end])
    except json.JSONDecodeError:
        return []


def is_spanish(user_content: str) -> bool:
    """Heuristic: detect Spanish by common markers."""
    msg = user_content.split("USER: ")[-1].lower() if "USER: " in user_content else user_content.lower()
    es_markers = [
        "el ", "la ", "los ", "las ", "del ", "al ", "que ", "con ",
        "por ", "para ", "está ", "tiene ", "vamos", "tengo", "necesito",
        "cómo", "qué", "podés", "estoy", "quiero", "nos ", "mi ",
        "ojo", "dale", "bueno", "hola", "che ", "bien", "ayer",
        "plata", "terreno", "obra", "sueldo", "viaje", "nene",
        "barrio", "fondo", "corregime", "ampliame", "contame",
        "resumime", "seguí", "decime", "metí", "cobro",
    ]
    return any(m in msg for m in es_markers)


def main():
    random.seed(42)

    print("=" * 60)
    print("Merging V4 Training Dataset")
    print("=" * 60)

    # --- Load all group files ---
    print("\n--- Loading skill groups ---")
    all_examples = []
    group_files = sorted(V4_DIR.glob("v4_g*.jsonl"))
    group_counts = {}

    for path in group_files:
        examples = load_jsonl(path)
        group_name = path.stem
        group_counts[group_name] = len(examples)
        print(f"  {path.name}: {len(examples)}")
        all_examples.extend(examples)

    print(f"\n  Total loaded: {len(all_examples)}")

    # --- Validate all against V4 schema ---
    print("\n--- Schema Validation ---")
    schema_ok = 0
    xref_ok = 0
    schema_errors = []
    xref_errors = []
    null_entity_ids = 0

    for i, ex in enumerate(all_examples):
        assistant_content = ex["messages"][2]["content"]

        # Schema validation
        ok, result = validate_s1_v4(assistant_content)
        if ok:
            schema_ok += 1
        else:
            schema_errors.append((i + 1, result))
            continue

        # Cross-reference validation
        existing_nodes = parse_existing_nodes(ex["messages"][1]["content"])
        output = json.loads(assistant_content)
        xr_errs = validate_cross_references(output, existing_nodes)
        if not xr_errs:
            xref_ok += 1
        else:
            xref_errors.append((i + 1, xr_errs))

        # Null entity_id check
        for f in output.get("facts", []):
            if not f.get("entity_id"):
                null_entity_ids += 1

    print(f"  Schema valid: {schema_ok}/{len(all_examples)} ({schema_ok/len(all_examples)*100:.1f}%)")
    print(f"  XRef valid:   {xref_ok}/{len(all_examples)} ({xref_ok/len(all_examples)*100:.1f}%)")
    print(f"  Null entity_id: {null_entity_ids}")

    if schema_errors:
        print(f"\n  Schema errors ({len(schema_errors)}):")
        for idx, err in schema_errors[:5]:
            print(f"    Example {idx}: {err}")

    if xref_errors:
        print(f"\n  XRef errors ({len(xref_errors)}):")
        for idx, errs in xref_errors[:5]:
            for e in errs:
                print(f"    Example {idx}: {e}")

    # --- Dedup ---
    seen = set()
    deduped = []
    dupes = 0
    for ex in all_examples:
        h = example_hash(ex)
        if h not in seen:
            seen.add(h)
            deduped.append(ex)
        else:
            dupes += 1

    if dupes:
        print(f"\n  Removed {dupes} duplicates")
    print(f"  After dedup: {len(deduped)} examples")

    # --- Split train/val ---
    random.shuffle(deduped)
    val_count = max(1, int(len(deduped) * VAL_SPLIT))
    val_examples = deduped[:val_count]
    train_examples = deduped[val_count:]

    print(f"\n  Train: {len(train_examples)}")
    print(f"  Val:   {len(val_examples)}")

    # --- Write ---
    random.shuffle(train_examples)
    random.shuffle(val_examples)

    with open(TRAIN_OUTPUT, "w", encoding="utf-8") as f:
        for ex in train_examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    print(f"\n  Wrote {TRAIN_OUTPUT.name}")

    with open(VAL_OUTPUT, "w", encoding="utf-8") as f:
        for ex in val_examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    print(f"  Wrote {VAL_OUTPUT.name}")

    # --- Comprehensive Stats ---
    print("\n" + "=" * 60)
    print("FINAL DATASET STATISTICS")
    print("=" * 60)

    all_final = train_examples + val_examples
    total = len(all_final)

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
    english = 0

    for ex in all_final:
        output = json.loads(ex["messages"][2]["content"])
        intents[output["intent"]["type"]] += 1
        retrievals[output["intent"]["retrieval"]] += 1
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
        for rel in rels:
            relation_types[rel.get("relation", "?")] += 1

        # Language
        if is_spanish(ex["messages"][1]["content"]):
            spanish += 1
        else:
            english += 1

    print(f"\nTotal: {total} (train: {len(train_examples)}, val: {len(val_examples)})")

    print(f"\nSkill group distribution:")
    for name, count in sorted(group_counts.items()):
        pct = count / total * 100
        bar = "#" * int(pct / 2)
        print(f"  {name:30s}: {count:4d} ({pct:5.1f}%) {bar}")

    print(f"\nLanguage: Spanish={spanish} ({spanish*100/total:.1f}%), "
          f"English={english} ({english*100/total:.1f}%)")

    print(f"\nIntent distribution:")
    for intent, count in sorted(intents.items(), key=lambda x: -x[1]):
        pct = count / total * 100
        bar = "#" * int(pct / 2)
        print(f"  {intent:12s}: {count:4d} ({pct:5.1f}%) {bar}")

    print(f"\nRetrieval distribution:")
    for ret, count in sorted(retrievals.items(), key=lambda x: -x[1]):
        pct = count / total * 100
        print(f"  {ret:14s}: {count:4d} ({pct:5.1f}%)")

    print(f"\nTopic action distribution:")
    for action, count in sorted(topics.items(), key=lambda x: -x[1]):
        pct = count / total * 100
        print(f"  {action:12s}: {count:4d} ({pct:5.1f}%)")

    print(f"\nExtraction content:")
    print(f"  With entities:  {has_entities:4d} ({has_entities*100/total:.1f}%)")
    print(f"  With relations: {has_relations:4d} ({has_relations*100/total:.1f}%)")
    print(f"  With facts:     {has_facts:4d} ({has_facts*100/total:.1f}%)")
    print(f"  Avg entities/ex: {total_entities/total:.2f}")
    print(f"  Avg relations/ex: {total_relations/total:.2f}")
    print(f"  Avg facts/ex: {total_facts/total:.2f}")

    print(f"\nEntity types ({len(entity_types)}/8):")
    for etype, count in sorted(entity_types.items(), key=lambda x: -x[1]):
        print(f"  {etype:15s}: {count:4d}")

    print(f"\nRelation types ({len(relation_types)}/16):")
    all_rel_types = {rt.value for rt in RelationType}
    covered = set(relation_types.keys())
    missing = all_rel_types - covered
    for rtype, count in sorted(relation_types.items(), key=lambda x: -x[1]):
        print(f"  {rtype:18s}: {count:4d}")
    if missing:
        print(f"\n  MISSING relations: {', '.join(sorted(missing))}")

    # --- Quality Checks ---
    print("\n" + "=" * 60)
    print("QUALITY CHECKS")
    print("=" * 60)
    all_ok = True

    # Check: all schema valid
    if schema_ok < len(all_examples):
        print(f"  FAIL: {len(all_examples) - schema_ok} schema validation failures")
        all_ok = False
    else:
        print(f"  PASS: All {schema_ok} examples schema valid")

    # Check: all cross-refs valid
    if xref_ok < schema_ok:
        print(f"  FAIL: {schema_ok - xref_ok} cross-reference failures")
        all_ok = False
    else:
        print(f"  PASS: All {xref_ok} cross-references valid")

    # Check: zero null entity_id
    if null_entity_ids > 0:
        print(f"  FAIL: {null_entity_ids} facts with null/empty entity_id")
        all_ok = False
    else:
        print(f"  PASS: Zero null entity_id in facts")

    # Check: all 16 relation types covered
    if len(covered) < 16:
        print(f"  WARN: Only {len(covered)}/16 relation types covered")
        all_ok = False
    else:
        print(f"  PASS: All 16 relation types covered")

    # Check: all 4 intents present
    if len(intents) < 4:
        print(f"  FAIL: Only {len(intents)}/4 intent types present")
        all_ok = False
    else:
        print(f"  PASS: All 4 intent types present")

    # Check: language balance
    es_pct = spanish / total * 100
    if es_pct < 35:
        print(f"  WARN: Spanish only {es_pct:.1f}% (target: >40%)")
        all_ok = False
    else:
        print(f"  PASS: Spanish {es_pct:.1f}% (target: >40%)")

    # Check: fact coverage
    fact_pct = has_facts / total * 100
    if fact_pct < 40:
        print(f"  WARN: Only {fact_pct:.1f}% examples have facts")
    else:
        print(f"  PASS: {fact_pct:.1f}% examples have facts")

    if all_ok:
        print(f"\n  All quality checks PASSED")
    else:
        print(f"\n  Some checks need attention — review warnings above")

    print(f"\nOutput: {V4_DIR}")


if __name__ == "__main__":
    main()
