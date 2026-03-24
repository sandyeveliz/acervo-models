# Acervo Graph Model

Fine-tuning pipeline for **Qwen3.5-9B** — a specialized model that extracts structured knowledge graphs from conversations. Built for [Acervo](https://github.com/sandyeveliz/acervo), a semantic compression layer for AI agents.

**Model on Hugging Face:** [SandyVeliz/acervo-extractor-qwen3.5-9b](https://huggingface.co/SandyVeliz/acervo-extractor-qwen3.5-9b)

## Why this exists

Traditional RAG retrieves raw text chunks. Acervo replaces that with a compressed knowledge graph — structured nodes with entities, relations, and facts. This requires a fast, specialized model that can:

1. **Classify the conversation topic** (same / subtopic / changed)
2. **Extract entities** with types (person, project, technology, etc.) and layers (PERSONAL / UNIVERSAL)
3. **Map relations** between entities (uses_technology, part_of, works_at, etc.)
4. **Attach facts** to existing entities without creating duplicates
5. **Output valid JSON** — every time, no markdown, no explanation

A general-purpose LLM can do this but is slow and expensive. This fine-tuned 9B model does it in one pass with structured output.

## What the model does

**Input:** a conversation turn + existing graph nodes as context

**Output:** structured JSON

```json
{
  "topic": {"action": "same"},
  "entities": [
    {"id": "kubernetes", "label": "Kubernetes", "type": "technology",
     "layer": "UNIVERSAL", "attributes": {}, "facts": [], "existing_id": null}
  ],
  "relations": [
    {"source": "beacon", "target": "kubernetes", "relation": "uses_technology"}
  ],
  "facts": [
    {"entity": "beacon", "text": "Has 50,000 users", "speaker": "user"}
  ]
}
```

The model handles bilingual input (English/Spanish), returns empty arrays for small talk (no hallucinated entities), and references existing graph nodes via `existing_id` to avoid duplicates.

## Project structure

```
00_setup/           GPU verification + dependency installation
01_dataset/         Pydantic schemas + dataset generation scripts
02_training/        SFT notebooks (initial + incremental)
03_eval/            Evaluation (WIP)
04_export/          Export to GGUF (WIP)
hf_upload/          Staging directory for Hugging Face uploads
training_data/      Generated JSONL datasets (gitignored)
```

## Schema

### Entity types
`person` · `organization` · `project` · `technology` · `place` · `event` · `document` · `concept`

### Relation types
`part_of` · `created_by` · `maintains` · `works_at` · `member_of` · `uses_technology` · `depends_on` · `alternative_to` · `located_in` · `deployed_on` · `produces` · `serves` · `documented_in` · `participated_in` · `triggered_by` · `resulted_in`

### Layers
- **PERSONAL** — user owns, created, or directly uses it
- **UNIVERSAL** — public knowledge (technologies, cities, fictional characters)

## Training pipeline

### 1. Setup (`00_setup/`)

- `check_gpu.ipynb` — verify GPU, CUDA, compute capability
- `install_deps.ipynb` — install dependencies in correct order (critical for Blackwell GPUs)

**Stack:** PyTorch cu128, unsloth, trl, bitsandbytes, peft

### 2. Dataset (`01_dataset/`)

- `schema.py` — Pydantic v2 schemas for S1 and S1.5 outputs, validation helpers, system prompts
- `generate_s1_training.py` — template-based generator: 450 train + 50 validation examples across 11 conversation types and 5 domains

**Dataset composition:**

| Type | % | Description |
|------|---|-------------|
| Facts on existing entities | 30% | New info about known nodes |
| New entity extraction | 20% | First mentions |
| Empty output (small talk/queries) | 15% | Must return `[]`, not hallucinate |
| Topic changes | 10% | Detecting new conversation topics |
| Subtopic shifts | 10% | Deeper into an aspect |
| Literary events | 5% | Narrative events with chronological markers |
| Corrections | 5% | "We switched from X to Y" |
| Dedup / existing refs | 5% | "nuestro proyecto" → existing_id |

### 3. Training (`02_training/`)

- `train_sft.ipynb` — initial SFT: LoRA r=16, alpha=32, lr=2e-4, 3 epochs on 450 examples
- `train_sft_continue.ipynb` — incremental SFT: loads existing LoRA, lr=5e-5, 2 epochs on 582 examples (original + supplementary + stress test)

**LoRA config:** 7 target modules, QLoRA 4-bit, adamw_8bit optimizer

### 4. Upload (`hf_upload/`)

- `prepare_and_upload.py` — copies LoRA + GGUF + training data to staging dir, uploads to HF
- `README.md` — model card with usage examples and metrics

## Hardware

| Component | Spec |
|-----------|------|
| GPU | NVIDIA RTX 5070 Ti (16GB VRAM, Blackwell sm_120) |
| CUDA | 12.8 (cu128) |
| PyTorch | nightly with cu128 backend |
| OS | Windows 11 |
| Training time | ~1h15m for 582 examples x 2 epochs |

## Quick start

```bash
# 1. Clone
git clone https://github.com/sandyeveliz/acervo-graph-model
cd acervo-graph-model

# 2. Setup (run notebooks in order)
#    00_setup/check_gpu.ipynb
#    00_setup/install_deps.ipynb

# 3. Generate training data
python 01_dataset/generate_s1_training.py --seed 42

# 4. Train
#    02_training/train_sft.ipynb

# 5. Upload to HF
pip install huggingface_hub
huggingface-cli login
python hf_upload/prepare_and_upload.py --upload --include-gguf --include-data
```

## Using the model

### With Unsloth (recommended)

```python
from unsloth import FastLanguageModel

model, tokenizer = FastLanguageModel.from_pretrained(
    "SandyVeliz/acervo-extractor-qwen3.5-9b",
    max_seq_length=2048, load_in_4bit=True,
)
FastLanguageModel.for_inference(model)
```

### With LM Studio / Ollama

Download the GGUF from the [HF repo](https://huggingface.co/SandyVeliz/acervo-extractor-qwen3.5-9b) and load it directly.

### With Acervo

```python
from acervo import Acervo, OpenAIClient

llm = OpenAIClient(base_url="http://localhost:1234/v1", model="acervo-extractor")
memory = Acervo(llm=llm, owner="user")
```

## Results

| Metric | v1 (450 examples) | v2 (582 examples) |
|--------|-------------------|-------------------|
| JSON parse rate | 95% | 100% |
| Stress test accuracy | 45% (9/20) | TBD |
| Training loss | 0.16 | TBD |

## License

Apache 2.0
