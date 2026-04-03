#!/usr/bin/env python3
"""
Migrate v1 training data to v2 schema by adding intent + retrieval fields.

Reads existing JSONL files and adds the correct `intent` and `retrieval`
fields to every assistant output based on heuristics derived from the
conversation type, user message, and output structure.

Writes augmented files to training_data/v2/ (originals are preserved).

Usage:
    python 01_dataset/add_intent_to_v1.py [--dry-run]
"""

import json
import re
import argparse
from pathlib import Path
from collections import Counter

# Input files (v1)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_DIR = PROJECT_ROOT / "training_data"
INPUT_FILES = [
    "s1_extraction.jsonl",
    "s1_validation.jsonl",
    "s1_suplementary_training.jsonl",
    "s1_stress_test.jsonl",
]

# Output directory (v2)
OUTPUT_DIR = PROJECT_ROOT / "training_data" / "v2"

# Updated system prompt (must match schema.py)
from schema import S1_SYSTEM_PROMPT as V2_SYSTEM_PROMPT

# ──────────────────────────────────────────────────────────────────────
# Heuristic classification
# ──────────────────────────────────────────────────────────────────────

CHAT_PATTERNS = re.compile(
    r"^("
    r"thanks?|thank you|thx|ty|"
    r"gracias|genial|dale|perfecto|buenísimo|buenisimo|"
    r"ok|okay|cool|nice|great|got it|understood|"
    r"sure|right|exactly|indeed|absolutely|"
    r"interesting|i see|noted|good|"
    r"lol|haha|jaja|"
    r"hello|hey|hi|hola|"
    r"bye|see you|chau|nos vemos|"
    r"good morning|good night|buen día|buenas noches|"
    r"that'?s (interesting|cool|nice|great|good|awesome)|"
    r"i think so|me too|same here|"
    r"no worries|don'?t worry|tranqui|"
    r"sounds good|sounds great|suena bien|"
    r"what do you think\??|"
    r"i agree|agreed|de acuerdo|"
    r"yeah|yep|sí|si|nah|nope"
    r")\.?!?\s*$",
    re.IGNORECASE
)

OVERVIEW_PATTERNS = re.compile(
    r"("
    r"what is (this|the) (project|app|application|system|book|document|repo)|"
    r"tell me about|"
    r"describe|"
    r"give me (a |an )?(summary|overview|resumen)|"
    r"how many|"
    r"what technologies|"
    r"list (all|the)|"
    r"what'?s the (overall|general)|"
    r"qué (es|sabés de|tecnologías)|"
    r"contame (de|sobre)|"
    r"dame un resumen|"
    r"cuántos|cuántas|"
    r"how is .+ going|"
    r"what does .+ (do|use)|"
    r"what about"
    r")",
    re.IGNORECASE
)

FOLLOWUP_PATTERNS = re.compile(
    r"("
    r"tell me more|"
    r"what else|"
    r"expand on|"
    r"go deeper|"
    r"more details|"
    r"contame más|"
    r"and what about|"
    r"y qué (hay de|pasa con)|"
    r"anything else|"
    r"also,?\s|"
    r"por cierto|"
    r"me olvidé|"
    r"ah,?\s|"
    r"oh,?\s(and|y)|"
    r"one more thing|"
    r"otra cosa"
    r")",
    re.IGNORECASE
)


def get_existing_node_ids(user_content: str) -> set[str]:
    """Extract existing node labels from the EXISTING NODES section."""
    labels = set()
    match = re.search(r"EXISTING NODES:\n(\[.+?\])\n", user_content, re.DOTALL)
    if match:
        try:
            nodes = json.loads(match.group(1))
            for n in nodes:
                labels.add(n.get("label", "").lower())
                labels.add(n.get("id", "").lower())
        except (json.JSONDecodeError, TypeError):
            pass
    return labels


def get_user_message(user_content: str) -> str:
    """Extract the USER: message from the formatted input."""
    match = re.search(r"USER:\s*(.+)$", user_content, re.DOTALL)
    return match.group(1).strip() if match else user_content


def get_prev_assistant(user_content: str) -> str | None:
    """Extract PREVIOUS ASSISTANT value."""
    match = re.search(r"PREVIOUS ASSISTANT:\s*(.+?)\nUSER:", user_content, re.DOTALL)
    if match:
        val = match.group(1).strip()
        return None if val == "null" else val
    return None


def get_current_topic(user_content: str) -> str | None:
    """Extract CURRENT TOPIC value."""
    match = re.search(r"CURRENT TOPIC:\s*(.+?)$", user_content, re.MULTILINE)
    if match:
        val = match.group(1).strip()
        return None if val == "null" else val
    return None


def has_question_mark(msg: str) -> bool:
    return "?" in msg


def references_specific_entity(msg: str, node_labels: set[str]) -> bool:
    """Check if the user message mentions a specific entity from the graph."""
    msg_lower = msg.lower()
    for label in node_labels:
        if label and len(label) > 2 and label in msg_lower:
            return True
    return False


def classify_intent_retrieval(
    user_content: str,
    output: dict,
    uncertain: list[str],
) -> tuple[str, str]:
    """
    Classify intent and retrieval for a v1 training example.

    Returns (intent, retrieval).
    """
    user_msg = get_user_message(user_content)
    prev_assistant = get_prev_assistant(user_content)
    node_labels = get_existing_node_ids(user_content)
    current_topic = get_current_topic(user_content)

    topic_action = output.get("topic", {}).get("action", "same")
    entities = output.get("entities", [])
    relations = output.get("relations", [])
    facts = output.get("facts", [])
    has_extraction = bool(entities or facts)
    is_empty = not entities and not relations and not facts

    # ── 1. Chat: empty output + casual pattern ──
    if is_empty and CHAT_PATTERNS.match(user_msg.strip()):
        return "chat", "summary_only"

    # Short casual messages without extraction
    if is_empty and len(user_msg.strip()) < 25 and not has_question_mark(user_msg):
        if not OVERVIEW_PATTERNS.search(user_msg):
            return "chat", "summary_only"

    # ── 2. Chat: small talk with opinions/emotions (longer but still empty) ──
    if is_empty and not has_question_mark(user_msg):
        chat_indicators = [
            "i think", "i believe", "i feel", "in my opinion",
            "creo que", "me parece", "opino que",
            "that's", "eso es", "qué bueno", "qué mal",
        ]
        if any(indicator in user_msg.lower() for indicator in chat_indicators):
            return "chat", "summary_only"

    # ── 3. Query with question mark + empty output → specific ──
    if is_empty and has_question_mark(user_msg):
        if OVERVIEW_PATTERNS.search(user_msg):
            return "overview", "summary_only"
        return "specific", "with_chunks"

    # ── 4. Overview: first message / topic change with broad intro ──
    if topic_action == "changed":
        # First messages (no current topic, no prev assistant)
        if not current_topic and not prev_assistant:
            return "overview", "summary_only"
        # Topic change — usually overview of the new topic
        if not references_specific_entity(user_msg, node_labels):
            return "overview", "summary_only"
        return "specific", "with_chunks"

    # ── 5. Followup: same topic with prev assistant ──
    if topic_action == "same" and prev_assistant:
        if FOLLOWUP_PATTERNS.search(user_msg):
            return "followup", "with_chunks" if has_extraction else "summary_only"
        # Adding new facts to existing topic = followup
        if has_extraction and not has_question_mark(user_msg):
            return "followup", "with_chunks"

    # ── 6. Subtopic → followup ──
    if topic_action == "subtopic":
        return "followup", "with_chunks" if has_extraction else "summary_only"

    # ── 7. Specific: references entities with question ──
    if has_question_mark(user_msg) and references_specific_entity(user_msg, node_labels):
        return "specific", "with_chunks"

    # ── 8. Same topic + new entities or facts, no question → specific (sharing info) ──
    if topic_action == "same" and has_extraction:
        # If user is providing information (not asking)
        if not has_question_mark(user_msg):
            if prev_assistant:
                return "followup", "with_chunks"
            return "specific", "with_chunks"
        return "specific", "with_chunks"

    # ── 9. Same topic + empty output + no question → chat ──
    if topic_action == "same" and is_empty and not has_question_mark(user_msg):
        return "chat", "summary_only"

    # ── Fallback: flag as uncertain ──
    uncertain.append(user_msg[:80])
    if has_question_mark(user_msg):
        return "specific", "with_chunks"
    if has_extraction:
        return "specific", "with_chunks"
    return "chat", "summary_only"


def augment_example(example: dict, uncertain: list[str]) -> dict:
    """Add intent + retrieval to a single training example."""
    user_content = example["messages"][1]["content"]
    output = json.loads(example["messages"][2]["content"])

    intent, retrieval = classify_intent_retrieval(user_content, output, uncertain)

    # Add new fields at the beginning of output
    augmented_output = {
        "intent": intent,
        "topic": output["topic"],
        "retrieval": retrieval,
        "entities": output.get("entities", []),
        "relations": output.get("relations", []),
        "facts": output.get("facts", []),
    }

    return {
        "messages": [
            {"role": "system", "content": V2_SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
            {"role": "assistant", "content": json.dumps(augmented_output, ensure_ascii=False)},
        ]
    }


def process_file(input_path: Path, output_path: Path, dry_run: bool) -> dict:
    """Process a single JSONL file. Returns stats."""
    examples = []
    intent_counts = Counter()
    retrieval_counts = Counter()
    uncertain = []

    with open(input_path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            example = json.loads(line)
            augmented = augment_example(example, uncertain)
            examples.append(augmented)

            output = json.loads(augmented["messages"][2]["content"])
            intent_counts[output["intent"]] += 1
            retrieval_counts[output["retrieval"]] += 1

    if not dry_run:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            for ex in examples:
                f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    return {
        "file": input_path.name,
        "total": len(examples),
        "intent": dict(intent_counts),
        "retrieval": dict(retrieval_counts),
        "uncertain_count": len(uncertain),
        "uncertain_samples": uncertain[:10],
    }


def main():
    parser = argparse.ArgumentParser(description="Add intent/retrieval to v1 training data")
    parser.add_argument("--dry-run", action="store_true", help="Only print stats, don't write files")
    args = parser.parse_args()

    print("=" * 60)
    print("v1 → v2 Training Data Migration")
    print("=" * 60)

    all_intent = Counter()
    all_retrieval = Counter()
    total_examples = 0
    total_uncertain = 0

    for filename in INPUT_FILES:
        input_path = INPUT_DIR / filename
        if not input_path.exists():
            print(f"\nSkipping {filename} (not found)")
            continue

        output_path = OUTPUT_DIR / filename
        stats = process_file(input_path, output_path, args.dry_run)

        print(f"\n--- {stats['file']} ({stats['total']} examples) ---")
        print(f"  Intent:    {stats['intent']}")
        print(f"  Retrieval: {stats['retrieval']}")
        print(f"  Uncertain: {stats['uncertain_count']}")
        if stats['uncertain_samples']:
            print(f"  Uncertain samples:")
            for s in stats['uncertain_samples']:
                print(f"    - {s}")

        all_intent.update(stats["intent"])
        all_retrieval.update(stats["retrieval"])
        total_examples += stats["total"]
        total_uncertain += stats["uncertain_count"]

    print("\n" + "=" * 60)
    print(f"TOTAL: {total_examples} examples")
    print(f"\nIntent distribution:")
    for intent, count in sorted(all_intent.items()):
        pct = count / total_examples * 100 if total_examples else 0
        print(f"  {intent:12s}: {count:4d} ({pct:.1f}%)")
    print(f"\nRetrieval distribution:")
    for ret, count in sorted(all_retrieval.items()):
        pct = count / total_examples * 100 if total_examples else 0
        print(f"  {ret:14s}: {count:4d} ({pct:.1f}%)")
    print(f"\nUncertain classifications: {total_uncertain}")

    # Cross-tab
    print(f"\nIntent x Retrieval cross-tab:")
    print(f"  {'':12s} | {'summary_only':>14s} | {'with_chunks':>14s}")
    print(f"  {'-'*12}-+-{'-'*14}-+-{'-'*14}")

    if not args.dry_run:
        print(f"\nOutput written to {OUTPUT_DIR}/")

        # Validate with schema
        print("\nValidating output against v2 schema...")
        from schema import validate_s1_jsonl
        for filename in INPUT_FILES:
            output_path = OUTPUT_DIR / filename
            if output_path.exists():
                stats = validate_s1_jsonl(str(output_path))
                status = "OK" if stats["schema_valid_rate"] == 1.0 else "FAIL"
                print(f"  {filename}: {status} ({stats['schema_valid_rate']:.0%} valid)")
                if stats["errors"]:
                    for line_num, err in stats["errors"][:3]:
                        print(f"    Line {line_num}: {err}")
    else:
        print("\n[DRY RUN — no files written]")


if __name__ == "__main__":
    main()
