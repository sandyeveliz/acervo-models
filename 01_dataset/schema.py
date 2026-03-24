"""
Pydantic schemas for Acervo graph model training data.

S1Output  — Unified extraction (topic classification + knowledge extraction)
S1_5Output — Graph update / curation post-response
"""

from __future__ import annotations

import json
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
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
    # Structure
    PART_OF = "part_of"
    CREATED_BY = "created_by"
    MAINTAINS = "maintains"
    WORKS_AT = "works_at"
    MEMBER_OF = "member_of"
    # Technology
    USES_TECHNOLOGY = "uses_technology"
    DEPENDS_ON = "depends_on"
    ALTERNATIVE_TO = "alternative_to"
    # Context
    LOCATED_IN = "located_in"
    DEPLOYED_ON = "deployed_on"
    PRODUCES = "produces"
    SERVES = "serves"
    DOCUMENTED_IN = "documented_in"
    # Events
    PARTICIPATED_IN = "participated_in"
    TRIGGERED_BY = "triggered_by"
    RESULTED_IN = "resulted_in"


class Layer(str, Enum):
    PERSONAL = "PERSONAL"
    UNIVERSAL = "UNIVERSAL"


# ---------------------------------------------------------------------------
# S1 Unified Output
# ---------------------------------------------------------------------------

class TopicResult(BaseModel):
    action: Literal["same", "subtopic", "changed"]
    label: str | None = None  # Only set when action is subtopic or changed


class EntityFact(BaseModel):
    text: str
    speaker: Literal["user", "assistant"] = "user"


class Entity(BaseModel):
    id: str  # snake_case
    label: str
    type: NodeType
    layer: Layer
    attributes: dict = Field(default_factory=dict)
    facts: list[EntityFact] = Field(default_factory=list)
    existing_id: str | None = None  # Set when this refers to an existing node


class Relation(BaseModel):
    source: str  # entity id
    target: str  # entity id
    relation: RelationType


class GraphFact(BaseModel):
    """New fact about an existing entity (not a new entity)."""
    entity: str  # existing node id
    text: str
    speaker: Literal["user", "assistant"] = "user"


class S1Output(BaseModel):
    topic: TopicResult
    entities: list[Entity] = Field(default_factory=list)
    relations: list[Relation] = Field(default_factory=list)
    facts: list[GraphFact] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# S1.5 Graph Update Output
# ---------------------------------------------------------------------------

class MergeAction(BaseModel):
    source_entity: str
    target_entity: str  # The one that "survives"
    reason: str


class TypeFix(BaseModel):
    entity: str
    old_type: str
    new_type: str


class S1_5Output(BaseModel):
    merges: list[MergeAction] = Field(default_factory=list)
    type_fixes: list[TypeFix] = Field(default_factory=list)
    discards: list[str] = Field(default_factory=list)
    assistant_entities: list[str] = Field(default_factory=list)
    assistant_facts: list[EntityFact] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def validate_s1(raw_json: str) -> tuple[bool, S1Output | str]:
    """Parse and validate S1 JSON. Returns (success, result_or_error)."""
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError as e:
        return False, f"JSON parse error: {e}"
    try:
        return True, S1Output.model_validate(data)
    except Exception as e:
        return False, f"Schema validation error: {e}"


def validate_s1_5(raw_json: str) -> tuple[bool, S1_5Output | str]:
    """Parse and validate S1.5 JSON. Returns (success, result_or_error)."""
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError as e:
        return False, f"JSON parse error: {e}"
    try:
        return True, S1_5Output.model_validate(data)
    except Exception as e:
        return False, f"Schema validation error: {e}"


def validate_s1_jsonl(path: str) -> dict:
    """Validate all examples in a JSONL file. Returns stats dict."""
    total = 0
    json_ok = 0
    schema_ok = 0
    errors = []

    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            total += 1
            try:
                example = json.loads(line)
                json_ok += 1
                assistant_content = example["messages"][2]["content"]
                ok, result = validate_s1(assistant_content)
                if ok:
                    schema_ok += 1
                else:
                    errors.append((i, result))
            except (json.JSONDecodeError, KeyError, IndexError) as e:
                errors.append((i, str(e)))

    return {
        "total": total,
        "json_parse_rate": json_ok / total if total else 0,
        "schema_valid_rate": schema_ok / total if total else 0,
        "errors": errors[:10],  # first 10 errors
    }


# ---------------------------------------------------------------------------
# System prompts
# ---------------------------------------------------------------------------

S1_SYSTEM_PROMPT = (
    "You are a knowledge extractor for a personal knowledge graph. "
    "Analyze the conversation and return a single JSON object with "
    "topic classification, entities, relations, and facts. "
    "Output valid JSON only, no markdown, no explanation."
)

S1_5_SYSTEM_PROMPT = (
    "You are the graph curator for a personal knowledge graph. "
    "Given the current graph state and the latest extraction, determine "
    "maintenance operations: merges (duplicates), type_fixes (misclassified), "
    "discards (noise). Return valid JSON only."
)


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Validate a sample S1 output (new format)
    sample_s1 = json.dumps({
        "topic": {"action": "same", "label": None},
        "entities": [
            {"id": "beacon", "label": "Beacon", "type": "project", "layer": "PERSONAL",
             "attributes": {}, "facts": [], "existing_id": None}
        ],
        "relations": [
            {"source": "beacon", "target": "react", "relation": "uses_technology"}
        ],
        "facts": [
            {"entity": "beacon", "text": "Has 50,000 monthly active users", "speaker": "user"}
        ],
    })
    ok, result = validate_s1(sample_s1)
    assert ok, f"S1 validation failed: {result}"
    print(f"OK - S1 sample valid: action={result.topic.action}, {len(result.entities)} entities")

    # Empty extraction
    sample_empty = json.dumps({
        "topic": {"action": "same", "label": None},
        "entities": [],
        "relations": [],
        "facts": [],
    })
    ok, result = validate_s1(sample_empty)
    assert ok, f"S1 empty validation failed: {result}"
    print(f"OK - S1 empty extraction valid")

    # Validate a sample S1.5 output
    sample_s1_5 = json.dumps({
        "merges": [{"source_entity": "la_base_de_datos", "target_entity": "firebase",
                     "reason": "alias contextual"}],
        "type_fixes": [],
        "discards": ["ruido_123"],
        "assistant_entities": ["nueva_entidad"],
        "assistant_facts": [{"text": "Firebase soporta realtime", "speaker": "user"}],
    })
    ok, result = validate_s1_5(sample_s1_5)
    assert ok, f"S1.5 validation failed: {result}"
    print(f"OK - S1.5 sample valid: {len(result.merges)} merges, {len(result.discards)} discards")

    # Validate training data if it exists
    from pathlib import Path
    train_path = Path("training_data/s1_extraction.jsonl")
    if train_path.exists():
        stats = validate_s1_jsonl(str(train_path))
        print(f"\nTraining data validation:")
        print(f"  Total: {stats['total']}")
        print(f"  JSON parse rate: {stats['json_parse_rate']:.1%}")
        print(f"  Schema valid rate: {stats['schema_valid_rate']:.1%}")
        if stats["errors"]:
            print(f"  First errors:")
            for line_num, err in stats["errors"][:3]:
                print(f"    Line {line_num}: {err}")
    else:
        print("\nNo training data found (run generate_s1_training.py first)")

    print("\nAll checks passed.")
