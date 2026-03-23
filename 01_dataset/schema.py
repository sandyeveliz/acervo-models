"""
Pydantic schemas for Acervo graph model training data.

S1Output  — Unified extraction (entities, relations, facts, events, topic management)
S1_5Output — Graph update / curation post-response
"""

from __future__ import annotations

import json
from typing import Literal

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# S1 Unified Output
# ---------------------------------------------------------------------------

class Relation(BaseModel):
    from_entity: str
    to_entity: str
    relation_type: str  # "uses", "belongs_to", "created_by", "similar_to", "depends_on", etc.
    confidence: float = Field(ge=0.0, le=1.0)


class Fact(BaseModel):
    text: str
    confidence: float = Field(ge=0.0, le=1.0)


class EventNode(BaseModel):
    """For book/document chunks with narrative events."""
    name: str
    participants: list[str] = Field(default_factory=list)
    location: str | None = None
    description: str
    temporal_marker: str | None = None  # "chapter 1", "after the war", "year 1991"
    source_chunk: str | None = None


class S1Output(BaseModel):
    # Topic management
    topic: str
    topic_action: Literal["same", "subtopic", "changed"]
    topic_confidence: float = Field(ge=0.0, le=1.0)

    # Extraction
    entities: list[str]
    relations: list[Relation] = Field(default_factory=list)
    facts: list[Fact] = Field(default_factory=list)
    events: list[EventNode] = Field(default_factory=list)

    # Metadata
    language: str  # "es", "en", etc.
    input_type: Literal["conversational", "document", "code"]


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
    assistant_facts: list[Fact] = Field(default_factory=list)


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


# ---------------------------------------------------------------------------
# System prompts for training data
# ---------------------------------------------------------------------------

S1_SYSTEM_PROMPT = (
    "Eres el motor de extracción de grafos de Acervo. "
    "Tu tarea es analizar el input y devolver ÚNICAMENTE un JSON válido "
    "sin texto adicional, sin markdown, sin explicaciones. /no_think"
)

S1_5_SYSTEM_PROMPT = (
    "Eres el curador de grafos de Acervo. "
    "Dado el estado actual del grafo y la extracción S1, determina qué operaciones "
    "de mantenimiento aplicar: merges (duplicados), type_fixes (tipos incorrectos), "
    "discards (ruido). Devuelve ÚNICAMENTE un JSON válido. /no_think"
)


# ---------------------------------------------------------------------------
# Chat template helpers (trl message format)
# ---------------------------------------------------------------------------

def make_s1_messages(
    user_msg: str,
    prev_assistant: str,
    topic_hint: str,
    graph_summary: dict,
    input_type: str,
    output: dict,
) -> dict:
    """Build a trl-compatible training example for S1."""
    user_content = (
        f"<task>S1_UNIFIED</task>\n"
        f"<input_type>{input_type}</input_type>\n"
        f"<user_msg>{user_msg}</user_msg>\n"
        f"<prev_assistant>{prev_assistant}</prev_assistant>\n"
        f"<topic_hint>{topic_hint}</topic_hint>\n"
        f"<graph_summary>{json.dumps(graph_summary, ensure_ascii=False)}</graph_summary>"
    )
    return {
        "messages": [
            {"role": "system", "content": S1_SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
            {"role": "assistant", "content": json.dumps(output, ensure_ascii=False)},
        ]
    }


def make_s1_5_messages(
    s1_entities: list[str],
    graph_nodes: dict,
    assistant_response: str,
    output: dict,
) -> dict:
    """Build a trl-compatible training example for S1.5."""
    user_content = (
        f"<task>S1_5_GRAPH_UPDATE</task>\n"
        f"<s1_entities>{json.dumps(s1_entities, ensure_ascii=False)}</s1_entities>\n"
        f"<graph_nodes>{json.dumps(graph_nodes, ensure_ascii=False)}</graph_nodes>\n"
        f"<assistant_response>{assistant_response}</assistant_response>"
    )
    return {
        "messages": [
            {"role": "system", "content": S1_5_SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
            {"role": "assistant", "content": json.dumps(output, ensure_ascii=False)},
        ]
    }


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Validate a sample S1 output
    sample_s1 = json.dumps({
        "topic": "trabajo",
        "topic_action": "same",
        "topic_confidence": 0.92,
        "entities": ["reunion_lunes", "marcos"],
        "relations": [
            {"from_entity": "reunion_lunes", "to_entity": "marcos",
             "relation_type": "involves", "confidence": 0.95}
        ],
        "facts": [{"text": "hay una reunión con Marcos el lunes", "confidence": 0.95}],
        "events": [],
        "language": "es",
        "input_type": "conversational",
    })
    ok, result = validate_s1(sample_s1)
    assert ok, f"S1 validation failed: {result}"
    print(f"OK - S1 sample valid: {result.topic_action}")

    # Validate a sample S1.5 output
    sample_s1_5 = json.dumps({
        "merges": [{"source_entity": "la_base_de_datos", "target_entity": "firebase",
                     "reason": "alias contextual"}],
        "type_fixes": [],
        "discards": ["ruido_123"],
        "assistant_entities": ["nueva_entidad"],
        "assistant_facts": [{"text": "Firebase soporta realtime", "confidence": 0.9}],
    })
    ok, result = validate_s1_5(sample_s1_5)
    assert ok, f"S1.5 validation failed: {result}"
    print(f"OK - S1.5 sample valid: {len(result.merges)} merges, {len(result.discards)} discards")

    # Test message formatting
    msg = make_s1_messages(
        user_msg="che, cómo va el bug de Butaco?",
        prev_assistant="Estamos revisándolo.",
        topic_hint="trabajo",
        graph_summary={"hot_nodes": ["butaco", "firebase"]},
        input_type="conversacional",
        output={"topic": "trabajo", "topic_action": "same", "topic_confidence": 0.9,
                "entities": ["butaco", "bug"], "relations": [], "facts": [],
                "events": [], "language": "es", "input_type": "conversational"},
    )
    assert len(msg["messages"]) == 3
    print(f"OK - S1 message format ({len(msg['messages'])} messages)")

    print("\nAll checks passed.")
