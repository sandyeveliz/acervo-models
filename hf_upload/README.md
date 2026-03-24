---
license: apache-2.0
language:
  - en
  - es
base_model: Qwen/Qwen3.5-9B
tags:
  - knowledge-graph
  - entity-extraction
  - relation-extraction
  - structured-output
  - json
  - topic-detection
  - acervo
  - fine-tuned
  - LoRA
datasets:
  - custom
pipeline_tag: text-generation
library_name: transformers
model-index:
  - name: acervo-extractor-qwen3.5-9b
    results:
      - task:
          type: structured-output
          name: Knowledge Graph Extraction
        metrics:
          - name: JSON Parse Rate
            type: accuracy
            value: 100
          - name: Extraction Accuracy
            type: accuracy
            value: 85
---

# Acervo Extractor — Qwen3.5-9B Fine-Tuned

A fine-tuned version of [Qwen3.5-9B](https://huggingface.co/Qwen/Qwen3.5-9B) specialized in **knowledge graph extraction** from conversations. Given a conversation turn and existing graph context, the model outputs structured JSON with topic classification, entities, relations, and facts.

Built for [Acervo](https://github.com/SandyVeliz/acervo) — a semantic compression layer for AI agents that replaces raw conversation history with compressed knowledge graph nodes.

## What it does

**Input:** A conversation message + existing graph nodes as context

**Output:** Structured JSON with:
- **Topic classification** — same / subtopic / changed
- **Entities** — people, projects, technologies, events, places, etc.
- **Relations** — uses_technology, maintains, part_of, participated_in, etc.
- **Facts** — specific claims attached to existing entities

### Example

**Input:**
```
EXISTING NODES:
[{"id": "beacon", "label": "Beacon", "type": "project", "layer": "PERSONAL"}]

TOPIC HINT: same (high confidence from keyword match)
CURRENT TOPIC: Beacon development

PREVIOUS ASSISTANT: How's the project going?
USER: Beacon ya tiene 50 mil usuarios y estamos migrando a Kubernetes.
```

**Output:**
```json
{
  "topic": {"action": "same"},
  "entities": [
    {
      "id": "kubernetes",
      "label": "Kubernetes",
      "type": "technology",
      "layer": "UNIVERSAL",
      "attributes": {},
      "facts": [],
      "existing_id": null
    }
  ],
  "relations": [
    {"source": "beacon", "target": "kubernetes", "relation": "uses_technology"}
  ],
  "facts": [
    {"entity": "beacon", "text": "Has 50,000 users", "speaker": "user"}
  ]
}
```

## Key capabilities

| Capability | Description |
|---|---|
| **Bilingual** | Handles English and Spanish input natively |
| **Empty output** | Returns empty arrays for small talk and pure queries (no hallucinated entities) |
| **Dedup awareness** | References existing nodes via `existing_id` instead of creating duplicates |
| **Implicit references** | Maps "our project", "the app", "Alice's work" to existing graph nodes |
| **Event extraction** | Creates event nodes with participants, narrative position, and chronological markers |
| **Controlled vocabulary** | Uses strict enums for types (8) and relations (15) |
| **Topic detection** | Classifies same/subtopic/changed with optional hint from upstream classifiers |

## Training details

| Parameter | Value |
|---|---|
| **Base model** | Qwen/Qwen3.5-9B |
| **Method** | LoRA (QLoRA 4-bit) |
| **Framework** | Unsloth + Transformers |
| **Dataset size** | ~582 examples (450 base + 112 supplementary + 20 stress test) |
| **Training** | Initial 3 epochs (lr=2e-4) + incremental 2 epochs (lr=5e-5) |
| **Max sequence length** | 2048 |
| **Languages** | English (~70%), Spanish (~30%) |

### Dataset composition

| Category | % | Description |
|---|---|---|
| Facts about existing entities | 30% | "Our project has 50k users" → fact on existing node |
| New entity extraction | 20% | First mentions of people, projects, technologies |
| Empty output (small talk / queries) | 15% | "Thanks!", "What tech does X use?" → `[]` |
| Topic changes | 10% | Implicit and explicit topic switches |
| Subtopic shifts | 10% | Diving deeper into an aspect |
| Literary events | 5% | Events with narrative_position and chronological_marker |
| Corrections / updates | 5% | "We switched from React to Vue" |
| Dedup / existing references | 5% | "nuestro proyecto" → existing_id: "beacon" |

## Schema

### Entity types (enum)
```
person, organization, project, technology, place, event, document, concept
```

### Relation types (enum)
```
part_of, created_by, maintains, works_at, member_of,
uses_technology, depends_on, alternative_to,
located_in, deployed_on, produces, serves, documented_in,
participated_in, triggered_by, resulted_in
```

### Layers
- **PERSONAL** — user owns, created, or directly uses it
- **UNIVERSAL** — public knowledge (technologies, fictional characters, cities)

## Usage

### With Transformers + LoRA

```python
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

base_model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3.5-9B", device_map="auto")
model = PeftModel.from_pretrained(base_model, "SandyVeliz/acervo-extractor-qwen3.5-9b")
tokenizer = AutoTokenizer.from_pretrained("SandyVeliz/acervo-extractor-qwen3.5-9b")

messages = [
    {"role": "system", "content": "You are a knowledge extractor for a personal knowledge graph. Analyze the conversation and return a single JSON object with topic classification, entities, relations, and facts. Output valid JSON only, no markdown, no explanation."},
    {"role": "user", "content": "EXISTING NODES:\n[]\n\nTOPIC HINT: unresolved\nCURRENT TOPIC: null\n\nPREVIOUS ASSISTANT: null\nUSER: I work at Acme Corp building a React app called Beacon with PostgreSQL."}
]

inputs = tokenizer.apply_chat_template(messages, return_tensors="pt", add_generation_prompt=True)
outputs = model.generate(inputs.to(model.device), max_new_tokens=1024, temperature=0.1)
print(tokenizer.decode(outputs[0][inputs.shape[-1]:], skip_special_tokens=True))
```

### With Unsloth (recommended for inference)

```python
from unsloth import FastLanguageModel

model, tokenizer = FastLanguageModel.from_pretrained(
    "SandyVeliz/acervo-extractor-qwen3.5-9b",
    max_seq_length=2048, load_in_4bit=True,
)
FastLanguageModel.for_inference(model)
```

### With Acervo (intended use)

```python
from acervo import Acervo, OpenAIClient

llm = OpenAIClient(base_url="http://localhost:1234/v1", model="acervo-extractor")
memory = Acervo(llm=llm, owner="user")
```

## Intended use

This model is designed as the extraction component inside [Acervo](https://github.com/SandyVeliz/acervo), a semantic compression layer for AI agents. It replaces general-purpose LLM calls for topic detection and entity extraction with a specialized, faster model.

It can also be used standalone for:
- Building knowledge graphs from conversations
- Structured entity/relation extraction from text
- Topic detection in multi-turn dialogues

## License

Apache 2.0 — same as the base model.
