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
  - intent-classification
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
  - name: acervo-extractor-v2
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

# Acervo Extractor v2

A fine-tuned version of [Qwen3.5-9B](https://huggingface.co/Qwen/Qwen3.5-9B) specialized in **knowledge graph extraction** from conversations. Given a conversation turn and existing graph context, the model outputs structured JSON with intent classification, topic detection, retrieval decision, entities, relations, and facts.

> **Base model:** Qwen3.5-9B | **Method:** QLoRA (4-bit, r=16, alpha=32) | **Training:** ~1,000 examples, 3 epochs

Built for [Acervo](https://github.com/SandyVeliz/acervo) — a semantic compression layer for AI agents that replaces raw conversation history with compressed knowledge graph nodes.

> **Supersedes:** [acervo-extractor-qwen3.5-9b](https://huggingface.co/SandyVeliz/acervo-extractor-qwen3.5-9b) (v1, deprecated)

## What's new in v2

v1 only handled topic detection and entity extraction. v2 adds **intent classification** and **retrieval decision** — two fields that were previously handled by regex/keyword heuristics outside the model.

| Feature | v1 | v2 |
|---|---|---|
| Topic detection | same / subtopic / changed | same / subtopic / changed |
| **Intent classification** | - | overview / specific / chat / followup |
| **Retrieval decision** | - | summary_only / with_chunks |
| Entity extraction | 8 types, 15 relations | 8 types, 15 relations |
| **Code extraction** | - | Extract entities from code snippets |
| **Document extraction** | - | Extract from READMEs, changelogs, docs |
| **Prose extraction** | - | Extract characters, locations from literature |
| Training examples | 612 | ~1,000 |
| S1 Intent accuracy | 78% | 92%+ (target) |

### Why intent matters

v1 benchmarks showed **78% intent accuracy** — the model classified overview questions as specific (6 out of 9 failures). This cascaded: wrong intent led to wrong retrieval strategy (56% S2 accuracy) and wrong budget allocation (32% S3 accuracy).

v2 trains the model to classify intent directly, replacing the external regex classifier.

### Why retrieval matters

The `retrieval` field tells the system whether to fetch full document chunks or just use node summaries:
- `summary_only` — for overview questions, chat, conceptual queries (cheaper, faster)
- `with_chunks` — for code lookups, specific facts, detailed analysis (needs raw content)

## Output schema

### v1 output (deprecated)
```json
{
  "topic": {"action": "same|changed|subtopic", "label": "..."},
  "entities": [...],
  "relations": [...],
  "facts": [...]
}
```

### v2 output (new fields highlighted)
```json
{
  "intent": "overview|specific|chat|followup",     // NEW
  "topic": {"action": "same|changed|subtopic", "label": "..."},
  "retrieval": "summary_only|with_chunks",          // NEW
  "entities": [...],
  "relations": [...],
  "facts": [...]
}
```

## Intent types

| Intent | Description | Examples |
|---|---|---|
| `overview` | High-level summary, counts, listings, general info | "What is this project?", "How many files?", "Give me a summary" |
| `specific` | Precise detail, specific code, particular fact | "How does auth work?", "Show me the controller", "What's the deadline?" |
| `chat` | Casual conversation, acknowledgments, opinions | "Thanks", "That's interesting", "Ok", "Good job" |
| `followup` | Continuing previous topic with more depth | "Tell me more", "What about the other one?", "Expand on that" |

## Examples

### Intent: overview
```
USER: What is this project about?
```
```json
{
  "intent": "overview",
  "topic": {"action": "same", "label": null},
  "retrieval": "summary_only",
  "entities": [],
  "relations": [],
  "facts": []
}
```

### Intent: specific (with extraction)
```
USER: Beacon ya tiene 50 mil usuarios y estamos migrando a Kubernetes.
```
```json
{
  "intent": "specific",
  "topic": {"action": "same", "label": null},
  "retrieval": "with_chunks",
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

### Intent: chat (empty output)
```
USER: That's interesting, thanks!
```
```json
{
  "intent": "chat",
  "topic": {"action": "same", "label": null},
  "retrieval": "summary_only",
  "entities": [],
  "relations": [],
  "facts": []
}
```

### Intent: followup
```
PREVIOUS ASSISTANT: The auth module uses JWT tokens with 24-hour expiry.
USER: Tell me more about that.
```
```json
{
  "intent": "followup",
  "topic": {"action": "same", "label": null},
  "retrieval": "with_chunks",
  "entities": [],
  "relations": [],
  "facts": []
}
```

## Key capabilities

| Capability | Description |
|---|---|
| **Intent classification** | Classifies user intent to drive retrieval strategy |
| **Retrieval decision** | Decides summary_only vs with_chunks for downstream pipeline |
| **Bilingual** | Handles English and Spanish input natively |
| **Empty output** | Returns empty arrays for small talk and pure queries (no hallucinated entities) |
| **Dedup awareness** | References existing nodes via `existing_id` instead of creating duplicates |
| **Code extraction** | Extracts technologies, patterns, and dependencies from code snippets |
| **Document extraction** | Extracts entities from READMEs, changelogs, sprint reviews, API docs |
| **Prose extraction** | Extracts characters, locations, events from literature and narratives |
| **Controlled vocabulary** | Uses strict enums for types (8) and relations (15) |
| **Topic detection** | Classifies same/subtopic/changed with optional hint from upstream classifiers |

## Training details

| Parameter | Value |
|---|---|
| **Base model** | Qwen/Qwen3.5-9B |
| **Method** | LoRA (QLoRA 4-bit, r=16, alpha=32) |
| **Framework** | Unsloth + Transformers + TRL |
| **Dataset size** | ~1,000 examples |
| **Training** | v1 base (3 epochs, lr=2e-4) + v2 incremental (2 epochs, lr=5e-5) + v3 intent+retrieval (3 epochs, lr=5e-5) |
| **Max sequence length** | 2048 |
| **Languages** | English (~65%), Spanish (~35%) |
| **Hardware** | NVIDIA RTX 5070 Ti (16GB VRAM) |

### Dataset composition

| Category | Count | Description |
|---|---|---|
| Conversation extraction (v1) | 350 | Facts, entities, relations from conversations |
| Topic detection (v1) | 120 | Topic changes, subtopics |
| Empty output (v1) | 90 | Small talk, queries with no extraction |
| Corrections / dedup (v1) | 52 | "We switched from React to Vue", existing references |
| Stress / edge cases (v1) | 22 | Edge cases from v1 testing |
| **Intent classification (v2)** | **100** | Overview, specific, chat, followup examples |
| **Retrieval decision (v2)** | **80** | summary_only vs with_chunks |
| **Code extraction (v2)** | **50** | TypeScript, Python, YAML, Docker, SQL |
| **Literature extraction (v2)** | **40** | Characters, locations, events from prose |
| **Documentation extraction (v2)** | **40** | READMEs, changelogs, sprint reviews, API docs |
| **S1.5 improvement (v2)** | **30** | Extracting from assistant responses |
| **S1 failure variations (v2)** | **50** | Variations of 9 v0.4 benchmark failures |

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

### With LM Studio / Ollama (GGUF)

Download the GGUF file from the `gguf/` folder and load in LM Studio. The model appears as **acervo-extractor-v2**.

### With Transformers + LoRA

```python
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

base_model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3.5-9B", device_map="auto")
model = PeftModel.from_pretrained(base_model, "SandyVeliz/acervo-extractor-v2")
tokenizer = AutoTokenizer.from_pretrained("SandyVeliz/acervo-extractor-v2")

messages = [
    {"role": "system", "content": "You are a knowledge extractor for a personal knowledge graph. Analyze the conversation and return a single JSON object with: intent, topic, retrieval, entities, relations, and facts.\n\nIntent — classify the user's intent:\n- \"overview\": user wants a high-level summary, project description, general information, counts, or listings.\n- \"specific\": user wants a precise detail, specific code, a particular fact, or a specific section.\n- \"chat\": casual conversation, greetings, acknowledgments, opinions, or thanks.\n- \"followup\": continuing the previous topic with more depth, \"tell me more\", or referencing something just discussed.\n\nRetrieval — decide what data the system should fetch:\n- \"summary_only\": the node summary is enough (overview, chat, conceptual questions).\n- \"with_chunks\": the user needs specific content from documents (code lookups, specific facts, detailed analysis).\n\nOutput valid JSON only, no markdown, no explanation."},
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
    "SandyVeliz/acervo-extractor-v2",
    max_seq_length=2048, load_in_4bit=True,
)
FastLanguageModel.for_inference(model)
```

### With Acervo (intended use)

```python
from acervo import Acervo, OpenAIClient

llm = OpenAIClient(base_url="http://localhost:1234/v1", model="acervo-extractor-v2")
memory = Acervo(llm=llm, owner="user")
```

## Intended use

This model is designed as the extraction component inside [Acervo](https://github.com/SandyVeliz/acervo), a semantic compression layer for AI agents. It replaces general-purpose LLM calls for topic detection, intent classification, and entity extraction with a specialized, faster model.

It can also be used standalone for:
- Building knowledge graphs from conversations
- Structured entity/relation extraction from text
- Topic detection in multi-turn dialogues
- Intent classification for conversational AI
- Retrieval strategy decisions (RAG pipelines)

## Version history

| Version | Repo | Examples | Key changes |
|---|---|---|---|
| v1 | [acervo-extractor-qwen3.5-9b](https://huggingface.co/SandyVeliz/acervo-extractor-qwen3.5-9b) | 612 | Topic detection + entity extraction |
| **v2** | **acervo-extractor-v2** | **~1,000** | **+ Intent classification, retrieval decision, code/doc/prose extraction** |

## License

Apache 2.0 — same as the base model.
