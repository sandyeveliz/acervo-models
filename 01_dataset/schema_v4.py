"""
Pydantic schemas for Acervo graph model V4 training data.

V4 schema changes from V3:
  - intent is now an object: {"type": "...", "retrieval": "..."}
  - entities have "description" instead of "attributes" + inline "facts"
  - ALL facts go to top-level facts[] with "entity_id" key (was "entity")
  - topic.label is ALWAYS present (was null when action="same")
"""

from __future__ import annotations

import json
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, model_validator


# ---------------------------------------------------------------------------
# Enums (same as schema.py)
# ---------------------------------------------------------------------------

class NodeType(str, Enum):
    PERSON = "person"
    ORGANIZATION = "organization"
    PROJECT = "project"
    TECHNOLOGY = "technology"
    PLACE = "place"
    EVENT = "event"
    DOCUMENT = "document"
    CONCEPT = "concept"


class RelationType(str, Enum):
    PART_OF = "part_of"
    CREATED_BY = "created_by"
    MAINTAINS = "maintains"
    WORKS_AT = "works_at"
    MEMBER_OF = "member_of"
    USES_TECHNOLOGY = "uses_technology"
    DEPENDS_ON = "depends_on"
    ALTERNATIVE_TO = "alternative_to"
    LOCATED_IN = "located_in"
    DEPLOYED_ON = "deployed_on"
    PRODUCES = "produces"
    SERVES = "serves"
    DOCUMENTED_IN = "documented_in"
    PARTICIPATED_IN = "participated_in"
    TRIGGERED_BY = "triggered_by"
    RESULTED_IN = "resulted_in"


class Layer(str, Enum):
    PERSONAL = "PERSONAL"
    UNIVERSAL = "UNIVERSAL"


# ---------------------------------------------------------------------------
# S1 V4 Output Models
# ---------------------------------------------------------------------------

class TopicResult(BaseModel):
    action: Literal["same", "subtopic", "changed"]
    label: str  # ALWAYS present — short topic label

class IntentResult(BaseModel):
    type: Literal["overview", "specific", "chat", "followup"]
    retrieval: Literal["summary_only", "with_chunks"]

class EntityV4(BaseModel):
    id: str
    label: str
    type: NodeType
    layer: Layer
    description: str
    existing_id: str | None = None

class RelationV4(BaseModel):
    source: str
    target: str
    relation: RelationType

class GraphFactV4(BaseModel):
    entity_id: str
    text: str
    speaker: Literal["user", "assistant"] = "user"

class S1V4Output(BaseModel):
    topic: TopicResult
    intent: IntentResult
    entities: list[EntityV4] = Field(default_factory=list)
    relations: list[RelationV4] = Field(default_factory=list)
    facts: list[GraphFactV4] = Field(default_factory=list)

    @model_validator(mode="after")
    def no_null_entity_ids(self) -> "S1V4Output":
        for f in self.facts:
            if not f.entity_id:
                raise ValueError(f"Fact has empty/null entity_id: {f.text!r}")
        return self


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def validate_s1_v4(raw_json: str) -> tuple[bool, S1V4Output | str]:
    """Parse and validate V4 S1 JSON. Returns (success, result_or_error)."""
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError as e:
        return False, f"JSON parse error: {e}"
    try:
        return True, S1V4Output.model_validate(data)
    except Exception as e:
        return False, f"Schema validation error: {e}"


def validate_cross_references(
    output: dict,
    existing_nodes: list[dict],
) -> list[str]:
    """Check that entity_id/existing_id/source/target resolve to valid IDs.

    Returns list of error strings (empty = all good).
    """
    errors: list[str] = []
    existing_ids = {n["id"] for n in existing_nodes}
    new_ids = {e["id"] for e in output.get("entities", [])}
    all_ids = existing_ids | new_ids

    # Facts must reference valid entity_id
    for f in output.get("facts", []):
        eid = f.get("entity_id")
        if not eid:
            errors.append(f"Fact has null/empty entity_id: {f.get('text', '')!r}")
        elif eid not in all_ids:
            errors.append(f"Fact entity_id={eid!r} not in existing nodes or new entities")

    # existing_id on entities must point to existing nodes
    for e in output.get("entities", []):
        ex_id = e.get("existing_id")
        if ex_id and ex_id not in existing_ids:
            errors.append(f"Entity {e['id']!r} has existing_id={ex_id!r} not in existing nodes")

    # Relation source/target must be valid IDs
    for r in output.get("relations", []):
        if r["source"] not in all_ids:
            errors.append(f"Relation source={r['source']!r} not found")
        if r["target"] not in all_ids:
            errors.append(f"Relation target={r['target']!r} not found")

    return errors


def validate_s1_v4_jsonl(path: str) -> dict:
    """Validate all examples in a JSONL file. Returns stats dict."""
    total = 0
    json_ok = 0
    schema_ok = 0
    xref_ok = 0
    errors = []

    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            total += 1
            try:
                example = json.loads(line)
                json_ok += 1

                assistant_content = example["messages"][2]["content"]
                ok, result = validate_s1_v4(assistant_content)
                if ok:
                    schema_ok += 1
                else:
                    errors.append((i, result))
                    continue

                # Cross-reference validation
                user_content = example["messages"][1]["content"]
                existing_nodes = _parse_existing_nodes(user_content)
                output = json.loads(assistant_content)
                xref_errors = validate_cross_references(output, existing_nodes)
                if not xref_errors:
                    xref_ok += 1
                else:
                    errors.append((i, "; ".join(xref_errors)))

            except (json.JSONDecodeError, KeyError, IndexError) as e:
                errors.append((i, str(e)))

    return {
        "total": total,
        "json_parse_rate": json_ok / total if total else 0,
        "schema_valid_rate": schema_ok / total if total else 0,
        "xref_valid_rate": xref_ok / total if total else 0,
        "errors": errors[:20],
    }


def _parse_existing_nodes(user_content: str) -> list[dict]:
    """Extract existing nodes JSON from user message content."""
    prefix = "EXISTING NODES:\n"
    if prefix not in user_content:
        return []
    start = user_content.index(prefix) + len(prefix)
    # Find end of JSON array (next double newline)
    end = user_content.find("\n\n", start)
    if end == -1:
        end = len(user_content)
    try:
        return json.loads(user_content[start:end])
    except json.JSONDecodeError:
        return []


# ---------------------------------------------------------------------------
# System prompt — exact copy from production
# ---------------------------------------------------------------------------

S1_V4_SYSTEM_PROMPT = """\
You are a knowledge graph extractor. You receive a conversation turn and existing graph context, and output ONLY a JSON object. No explanation, no markdown, no preamble.

## Your task

Analyze the conversation and extract:
1. The topic status relative to the previous turn
2. New or updated entities mentioned IN THE CONVERSATION
3. Relations between entities
4. New facts about existing entities
5. The user's intent and retrieval needs

## Output schema

{
  "topic": {
    "action": "same | subtopic | changed",
    "label": "short topic label"
  },
  "intent": {
    "type": "overview | specific | followup | chat",
    "retrieval": "summary_only | with_chunks"
  },
  "entities": [
    {
      "id": "lowercase_snake_case",
      "label": "Display Name",
      "type": "person | organization | project | technology | place | event | document | concept",
      "layer": "PERSONAL | UNIVERSAL",
      "description": "One sentence description",
      "existing_id": null
    }
  ],
  "relations": [
    {
      "source": "entity_id",
      "target": "entity_id",
      "relation": "part_of | created_by | maintains | works_at | member_of | uses_technology | depends_on | alternative_to | located_in | deployed_on | produces | serves | documented_in | participated_in | triggered_by | resulted_in"
    }
  ],
  "facts": [
    {
      "entity_id": "existing_entity_id",
      "text": "The specific fact",
      "speaker": "user | assistant"
    }
  ]
}

## CRITICAL RULES

### Entity rules
- Extract ONLY entities that are explicitly mentioned in the current conversation turn
- DO NOT invent, guess, or hallucinate entities that are not in the text
- DO NOT generate entities from your training data or general knowledge
- ONLY use these types: person, organization, project, technology, place, event, document, concept
- If unsure between types, use "concept"
- Use "existing_id" when the entity already exists in the provided graph context \u2014 do NOT create duplicates
- PERSONAL = user owns it, created it, works on it, or it's specific to their life/work
- UNIVERSAL = public knowledge (programming languages, cities, famous people, general concepts)
- Generate "id" as lowercase_snake_case derived from the label
- Do NOT extract the user or assistant themselves as entities

### Fact rules \u2014 READ CAREFULLY
- Facts are specific data points, numbers, dates, amounts, decisions, or status updates mentioned in the conversation
- EVERY fact MUST have a valid entity_id \u2014 NEVER return entity_id as null, empty, or missing
- If a fact doesn't clearly belong to an existing entity, create a new entity for it first, then attach the fact
- Numeric data is ALWAYS a fact: prices, salaries, dates, percentages, quantities, measurements
- Decisions are facts: "decidimos ir con X", "elegimos Y", "compramos Z"
- Progress updates are facts: "ya tenemos X", "faltan Y", "llevamos Z gastados"
- Keep facts concise but include the specific numbers
- Do NOT duplicate facts already present in the graph context
- Attribute to "user" or "assistant" based on who stated it

### Relation rules
- ONLY use the 16 relations listed in the schema above
- If no listed relation fits, do NOT create the relation \u2014 skip it entirely
- Common WRONG relations that you must NOT use: near, visited, has, needs, says, uses, owns, supports, proposes, implemented, works_with, has_document, departures_from, arrives_at
- Source and target must both be entity IDs (either new or existing)
- Do NOT create self-referential relations

### When to return empty arrays
- Greetings, small talk, meta-questions about the AI \u2192 entities: [], relations: [], facts: []
- Questions that only READ from the graph without adding info \u2192 entities: [], relations: [], facts: []
- Do NOT hallucinate entities to fill the output \u2014 empty is better than wrong"""


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Test 1: Valid S1V4 output with entities and facts
    sample = json.dumps({
        "topic": {"action": "same", "label": "beacon project"},
        "intent": {"type": "specific", "retrieval": "summary_only"},
        "entities": [
            {"id": "sarah_chen", "label": "Sarah Chen", "type": "person",
             "layer": "PERSONAL", "description": "New tech lead for Beacon",
             "existing_id": None}
        ],
        "relations": [
            {"source": "sarah_chen", "target": "beacon", "relation": "maintains"}
        ],
        "facts": [
            {"entity_id": "sarah_chen", "text": "Salary: 180k USD/year", "speaker": "user"},
            {"entity_id": "beacon", "text": "New tech lead: Sarah Chen", "speaker": "user"},
        ],
    })
    ok, result = validate_s1_v4(sample)
    assert ok, f"V4 validation failed: {result}"
    print(f"OK - V4 sample valid: {len(result.entities)} entities, {len(result.facts)} facts")

    # Test 2: Empty extraction
    sample_empty = json.dumps({
        "topic": {"action": "same", "label": "general"},
        "intent": {"type": "chat", "retrieval": "summary_only"},
        "entities": [], "relations": [], "facts": [],
    })
    ok, result = validate_s1_v4(sample_empty)
    assert ok, f"V4 empty validation failed: {result}"
    print("OK - V4 empty extraction valid")

    # Test 3: Null entity_id should FAIL
    sample_null = json.dumps({
        "topic": {"action": "same", "label": "test"},
        "intent": {"type": "specific", "retrieval": "summary_only"},
        "entities": [], "relations": [],
        "facts": [{"entity_id": "", "text": "some fact", "speaker": "user"}],
    })
    ok, result = validate_s1_v4(sample_null)
    assert not ok, "V4 should reject empty entity_id"
    print(f"OK - V4 correctly rejected empty entity_id: {result}")

    # Test 4: Cross-reference validation
    existing = [
        {"id": "beacon", "label": "Beacon", "type": "Project", "facts": ["React frontend"]},
        {"id": "acme_corp", "label": "Acme Corp", "type": "Organization"},
    ]
    output = json.loads(sample)
    xref_errors = validate_cross_references(output, existing)
    assert not xref_errors, f"Cross-ref errors: {xref_errors}"
    print("OK - Cross-reference validation passed")

    # Test 5: Cross-ref should catch bad entity_id
    bad_output = {
        "entities": [], "relations": [],
        "facts": [{"entity_id": "nonexistent", "text": "bad fact", "speaker": "user"}],
    }
    xref_errors = validate_cross_references(bad_output, existing)
    assert len(xref_errors) == 1, f"Should have 1 error, got: {xref_errors}"
    print(f"OK - Cross-ref caught bad entity_id: {xref_errors[0]}")

    # Test 6: Invalid relation type should FAIL
    sample_bad_rel = json.dumps({
        "topic": {"action": "same", "label": "test"},
        "intent": {"type": "specific", "retrieval": "summary_only"},
        "entities": [], "facts": [],
        "relations": [{"source": "a", "target": "b", "relation": "near"}],
    })
    ok, result = validate_s1_v4(sample_bad_rel)
    assert not ok, "V4 should reject invalid relation type 'near'"
    print(f"OK - V4 correctly rejected invalid relation: {result}")

    print("\nAll V4 schema checks passed.")
