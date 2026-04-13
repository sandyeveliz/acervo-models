#!/usr/bin/env python3
"""
Audit training data JSONL for common issues.
Usage: python audit_training_data.py <path_to_jsonl_or_directory>

If given a directory, scans all .jsonl files in it.
Outputs a markdown report to stdout.
"""

import json
import sys
import os
from collections import Counter, defaultdict
from pathlib import Path

VALID_TYPES = {"person", "organization", "project", "technology", "place", "event", "document", "concept"}
VALID_RELATIONS = {
    "part_of", "created_by", "maintains", "works_at", "member_of",
    "uses_technology", "depends_on", "alternative_to", "located_in",
    "deployed_on", "produces", "serves", "documented_in",
    "participated_in", "triggered_by", "resulted_in"
}
VALID_LAYERS = {"PERSONAL", "UNIVERSAL"}
VALID_INTENTS = {"overview", "specific", "followup", "chat"}
VALID_RETRIEVALS = {"summary_only", "with_chunks"}
VALID_TOPIC_ACTIONS = {"same", "subtopic", "changed"}

def load_jsonl(path):
    examples = []
    errors = []
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                examples.append((i, obj))
            except json.JSONDecodeError as e:
                errors.append((i, f"Invalid JSON: {e}"))
    return examples, errors


def parse_assistant_response(text):
    """Parse the assistant's response JSON from a training example."""
    try:
        return json.loads(text), None
    except json.JSONDecodeError as e:
        return None, str(e)


def audit_example(line_num, obj, filename):
    issues = []

    # Basic structure check
    msgs = obj.get("messages", [])
    if len(msgs) < 2:
        issues.append((line_num, "STRUCTURE", "Less than 2 messages"))
        return issues

    # Check roles
    roles = [m.get("role") for m in msgs]
    if roles[0] != "system":
        issues.append((line_num, "STRUCTURE", f"First message role is '{roles[0]}', expected 'system'"))
    if roles[-1] != "assistant":
        issues.append((line_num, "STRUCTURE", f"Last message role is '{roles[-1]}', expected 'assistant'"))

    # Parse assistant response
    assistant_msg = msgs[-1].get("content", "")
    response, parse_err = parse_assistant_response(assistant_msg)
    if parse_err:
        issues.append((line_num, "JSON_PARSE", f"Assistant response is not valid JSON: {parse_err}"))
        return issues

    # Parse user message to get existing nodes
    user_msg = ""
    for m in msgs:
        if m.get("role") == "user":
            user_msg = m.get("content", "")

    existing_ids = set()
    if "EXISTING NODES:" in user_msg:
        try:
            nodes_str = user_msg.split("EXISTING NODES:\n")[1].split("\n\nTOPIC")[0]
            existing_nodes = json.loads(nodes_str)
            existing_ids = {n["id"] for n in existing_nodes}
        except:
            pass

    # --- TOPIC ---
    topic = response.get("topic", {})
    if not topic:
        issues.append((line_num, "MISSING_FIELD", "No 'topic' field"))
    else:
        action = topic.get("action", "")
        if action not in VALID_TOPIC_ACTIONS:
            issues.append((line_num, "INVALID_VALUE", f"topic.action='{action}' not in {VALID_TOPIC_ACTIONS}"))
        if not topic.get("label"):
            issues.append((line_num, "MISSING_FIELD", "topic.label is empty"))

    # --- INTENT ---
    intent = response.get("intent", {})
    if not intent:
        issues.append((line_num, "MISSING_FIELD", "No 'intent' field"))
    else:
        intent_type = intent.get("type", "")
        if intent_type not in VALID_INTENTS:
            issues.append((line_num, "INVALID_VALUE", f"intent.type='{intent_type}' not in {VALID_INTENTS}"))
        retrieval = intent.get("retrieval", "")
        if retrieval not in VALID_RETRIEVALS:
            issues.append((line_num, "INVALID_VALUE", f"intent.retrieval='{retrieval}' not in {VALID_RETRIEVALS}"))

    # --- ENTITIES ---
    entities = response.get("entities", [])
    entity_ids_in_turn = set()
    for ent in entities:
        eid = ent.get("id", "")
        entity_ids_in_turn.add(eid)

        if not eid:
            issues.append((line_num, "EMPTY_ID", "Entity with empty id"))
        elif eid != eid.lower():
            issues.append((line_num, "ID_CASE", f"Entity id '{eid}' is not lowercase"))
        elif " " in eid:
            issues.append((line_num, "ID_SPACE", f"Entity id '{eid}' contains spaces"))

        etype = ent.get("type", "").lower()
        if etype not in VALID_TYPES:
            issues.append((line_num, "INVALID_TYPE", f"Entity '{eid}' has type '{ent.get('type')}' not in valid types"))

        layer = ent.get("layer", "")
        if layer and layer not in VALID_LAYERS:
            issues.append((line_num, "INVALID_LAYER", f"Entity '{eid}' has layer '{layer}' not in {VALID_LAYERS}"))

        if not ent.get("label"):
            issues.append((line_num, "MISSING_LABEL", f"Entity '{eid}' has no label"))

        # Check existing_id usage
        existing_id = ent.get("existing_id")
        if existing_id and existing_id not in existing_ids:
            issues.append((line_num, "BAD_EXISTING_ID", f"Entity '{eid}' references existing_id '{existing_id}' not in EXISTING NODES"))

        # Check if entity duplicates an existing node
        if eid in existing_ids and not existing_id:
            issues.append((line_num, "MISSING_EXISTING_ID", f"Entity '{eid}' matches existing node but existing_id is null"))

    # --- RELATIONS ---
    all_valid_ids = existing_ids | entity_ids_in_turn
    relations = response.get("relations", [])
    for rel in relations:
        src = rel.get("source", "")
        tgt = rel.get("target", "")
        rtype = rel.get("relation", "")

        if rtype not in VALID_RELATIONS:
            issues.append((line_num, "INVALID_RELATION", f"Relation '{rtype}' not in valid relations (src={src}, tgt={tgt})"))

        if src and src not in all_valid_ids:
            issues.append((line_num, "ORPHAN_REL_SRC", f"Relation source '{src}' not in entities or existing nodes"))
        if tgt and tgt not in all_valid_ids:
            issues.append((line_num, "ORPHAN_REL_TGT", f"Relation target '{tgt}' not in entities or existing nodes"))

        if src == tgt:
            issues.append((line_num, "SELF_REL", f"Self-referential relation: {src} → {tgt}"))

    # --- FACTS ---
    facts = response.get("facts", [])
    for fact in facts:
        entity_id = fact.get("entity_id", "") or fact.get("entity", "")
        text = fact.get("text", "")
        speaker = fact.get("speaker", "")

        if not entity_id:
            issues.append((line_num, "ORPHAN_FACT", f"Fact has no entity_id: '{text[:50]}...'"))
        elif entity_id not in all_valid_ids:
            issues.append((line_num, "ORPHAN_FACT", f"Fact entity_id '{entity_id}' not in entities or existing nodes: '{text[:50]}...'"))

        if not text:
            issues.append((line_num, "EMPTY_FACT", "Fact has empty text"))

        if speaker and speaker not in ("user", "assistant"):
            issues.append((line_num, "INVALID_SPEAKER", f"Fact speaker '{speaker}' not in (user, assistant)"))

    # --- CROSS-CHECKS ---
    # Check: user message mentions numbers but no facts extracted
    user_text = user_msg.lower()
    has_numbers = any(c.isdigit() for c in user_text)
    has_currency = any(w in user_text for w in ["usd", "ars", "$", "euros", "pesos", "dolares"])
    if has_numbers and has_currency and len(facts) == 0 and len(entities) > 0:
        issues.append((line_num, "MISSING_FACTS", "User message has numbers+currency but no facts extracted"))

    # Check: entities extracted but conversation is clearly small talk
    smalltalk_indicators = ["hola", "chau", "gracias", "thanks", "hello", "bye"]
    is_smalltalk = any(ind in user_text for ind in smalltalk_indicators) and len(user_text) < 100
    if is_smalltalk and len(entities) > 0:
        issues.append((line_num, "SMALLTALK_ENTITIES", f"Small talk but {len(entities)} entities extracted"))

    return issues


def audit_files(paths):
    all_issues = []
    file_stats = {}
    type_counter = Counter()
    relation_counter = Counter()
    intent_counter = Counter()
    topic_counter = Counter()
    total_examples = 0
    total_entities = 0
    total_relations = 0
    total_facts = 0
    empty_output_count = 0

    for path in paths:
        examples, parse_errors = load_jsonl(path)
        fname = os.path.basename(path)
        file_issues = []

        for line_num, err in parse_errors:
            file_issues.append((line_num, "JSON_PARSE", err))

        for line_num, obj in examples:
            total_examples += 1
            issues = audit_example(line_num, obj, fname)
            file_issues.extend(issues)

            # Stats
            msgs = obj.get("messages", [])
            if msgs and msgs[-1].get("role") == "assistant":
                try:
                    resp = json.loads(msgs[-1]["content"])
                    ents = resp.get("entities", [])
                    rels = resp.get("relations", [])
                    facts = resp.get("facts", [])
                    total_entities += len(ents)
                    total_relations += len(rels)
                    total_facts += len(facts)

                    if not ents and not rels and not facts:
                        empty_output_count += 1

                    for e in ents:
                        type_counter[e.get("type", "unknown").lower()] += 1
                    for r in rels:
                        relation_counter[r.get("relation", "unknown")] += 1

                    intent = resp.get("intent", {})
                    if isinstance(intent, dict):
                        intent_counter[intent.get("type", "missing")] += 1
                    elif isinstance(intent, str):
                        intent_counter[intent] += 1

                    topic = resp.get("topic", {})
                    if isinstance(topic, dict):
                        topic_counter[topic.get("action", "missing")] += 1
                except:
                    pass

        file_stats[fname] = {
            "examples": len(examples),
            "issues": len(file_issues),
            "parse_errors": len(parse_errors),
        }
        all_issues.extend([(fname, *issue) for issue in file_issues])

    return all_issues, file_stats, {
        "total_examples": total_examples,
        "total_entities": total_entities,
        "total_relations": total_relations,
        "total_facts": total_facts,
        "empty_output_count": empty_output_count,
        "type_distribution": type_counter,
        "relation_distribution": relation_counter,
        "intent_distribution": intent_counter,
        "topic_distribution": topic_counter,
    }


def print_report(all_issues, file_stats, global_stats):
    print("# Training Data Audit Report\n")

    # Global stats
    print("## Dataset Overview\n")
    print("| Metric | Value |")
    print("|--------|-------|")
    print(f"| Total examples | {global_stats['total_examples']} |")
    print(f"| Total entities | {global_stats['total_entities']} |")
    print(f"| Total relations | {global_stats['total_relations']} |")
    print(f"| Total facts | {global_stats['total_facts']} |")
    print(f"| Empty outputs | {global_stats['empty_output_count']} ({100*global_stats['empty_output_count']//max(1,global_stats['total_examples'])}%) |")
    print(f"| Total issues found | {len(all_issues)} |")
    print()

    # File breakdown
    print("## Per-file Summary\n")
    print("| File | Examples | Issues |")
    print("|------|----------|--------|")
    for fname, stats in sorted(file_stats.items()):
        print(f"| {fname} | {stats['examples']} | {stats['issues']} |")
    print()

    # Distribution tables
    print("## Entity Type Distribution\n")
    print("| Type | Count |")
    print("|------|-------|")
    for t, c in global_stats["type_distribution"].most_common():
        marker = " !!" if t not in VALID_TYPES else ""
        print(f"| {t}{marker} | {c} |")
    print()

    print("## Relation Distribution\n")
    print("| Relation | Count |")
    print("|----------|-------|")
    for r, c in global_stats["relation_distribution"].most_common():
        marker = " !!" if r not in VALID_RELATIONS else ""
        print(f"| {r}{marker} | {c} |")
    print()

    print("## Intent Distribution\n")
    print("| Intent | Count |")
    print("|--------|-------|")
    for i, c in global_stats["intent_distribution"].most_common():
        print(f"| {i} | {c} |")
    print()

    print("## Topic Action Distribution\n")
    print("| Action | Count |")
    print("|--------|-------|")
    for t, c in global_stats["topic_distribution"].most_common():
        print(f"| {t} | {c} |")
    print()

    # Issues by category
    issue_types = Counter(issue[2] for issue in all_issues)
    print("## Issues by Category\n")
    print("| Category | Count |")
    print("|----------|-------|")
    for cat, count in issue_types.most_common():
        print(f"| {cat} | {count} |")
    print()

    # Detailed issues (grouped by category)
    if all_issues:
        print("## Detailed Issues\n")
        by_category = defaultdict(list)
        for fname, line, cat, msg in all_issues:
            by_category[cat].append((fname, line, msg))

        for cat, items in sorted(by_category.items(), key=lambda x: -len(x[1])):
            print(f"### {cat} ({len(items)} issues)\n")
            for fname, line, msg in items[:20]:  # limit to 20 per category
                print(f"- `{fname}:{line}` -- {msg}")
            if len(items) > 20:
                print(f"- ... and {len(items) - 20} more")
            print()


def main():
    if len(sys.argv) < 2:
        print("Usage: python audit_training_data.py <path_to_jsonl_or_directory>")
        sys.exit(1)

    target = sys.argv[1]
    paths = []

    if os.path.isdir(target):
        for f in sorted(os.listdir(target)):
            if f.endswith(".jsonl"):
                paths.append(os.path.join(target, f))
    elif os.path.isfile(target):
        paths.append(target)
    else:
        print(f"Error: '{target}' not found")
        sys.exit(1)

    if not paths:
        print(f"No .jsonl files found in '{target}'")
        sys.exit(1)

    all_issues, file_stats, global_stats = audit_files(paths)
    print_report(all_issues, file_stats, global_stats)


if __name__ == "__main__":
    main()
