# Acervo Graph Model

Fine-tuning pipeline for **Qwen3.5-9B** — a specialized model that extracts structured knowledge graphs from conversations. Built for [Acervo](https://github.com/sandyeveliz/acervo), a semantic compression layer for AI agents.

**Latest model:** [SandyVeliz/acervo-extractor-v2](https://huggingface.co/SandyVeliz/acervo-extractor-v2)

## Why this exists

Traditional RAG retrieves raw text chunks. Acervo replaces that with a compressed knowledge graph — structured nodes with entities, relations, and facts. This requires a fast, specialized model that can:

1. **Classify user intent** (overview / specific / chat / followup)
2. **Decide retrieval strategy** (summary_only / with_chunks)
3. **Classify the conversation topic** (same / subtopic / changed)
4. **Extract entities** with types (person, project, technology, etc.) and layers (PERSONAL / UNIVERSAL)
5. **Map relations** between entities (uses_technology, part_of, works_at, etc.)
6. **Attach facts** to existing entities without creating duplicates
7. **Output valid JSON** — every time, no markdown, no explanation

A general-purpose LLM can do this but is slow and expensive. This fine-tuned 9B model does it in one pass with structured output.

## What the model outputs

```json
{
  "intent": "specific",
  "topic": {"action": "same"},
  "retrieval": "with_chunks",
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

## Project structure

```
00_setup/               GPU verification + dependency installation
01_dataset/
  schema.py             Pydantic schemas, system prompts, validation
  generate_s1_training.py       v1 dataset generator (612 examples)
  generate_s1_v2_training.py    v2 dataset generator (~390 new examples)
  add_intent_to_v1.py           Migrate v1 data to v2 schema
  merge_v2_dataset.py           Merge all data into final training set
  benchmark_failures.jsonl      9 S1 failures from v0.4 benchmarks
02_training/
  train_sft.ipynb               v1 initial SFT (450 examples, 3 epochs)
  train_sft_continue.ipynb      v1 incremental SFT (582 examples, 2 epochs)
  train_sft_v3.ipynb            v2 SFT with intent+retrieval (~1,000 examples, 3 epochs)
03_eval/
  eval_benchmarks.py            Benchmark evaluation + v1 vs v2 comparison
  eval_extraction.py            Indexed content extraction eval
hf_upload/
  prepare_and_upload.py         Upload LoRA + GGUF to HuggingFace
  README.md                     Model card
training_data/                  Generated JSONL datasets (gitignored)
```

## Version history

| Version | HF Model | Examples | Key changes |
|---------|----------|----------|-------------|
| v1 | [acervo-extractor-qwen3.5-9b](https://huggingface.co/SandyVeliz/acervo-extractor-qwen3.5-9b) (deprecated) | 612 | Topic detection + entity extraction |
| **v2** | **[acervo-extractor-v2](https://huggingface.co/SandyVeliz/acervo-extractor-v2)** | **~1,000** | **+ Intent classification, retrieval decision, code/doc/prose extraction** |

## How to train a new version

### Prerequisites
- NVIDIA GPU with 16GB+ VRAM (tested on RTX 5070 Ti)
- Python 3.12, CUDA 12.8
- Run `00_setup/check_gpu.ipynb` and `00_setup/install_deps.ipynb`

### Step 1: Update schema (if changing output format)

Edit `01_dataset/schema.py` — add/modify fields in `S1Output`, update `S1_SYSTEM_PROMPT`.

### Step 2: Generate training data

```bash
cd 01_dataset

# Migrate existing data to new schema (if schema changed)
python add_intent_to_v1.py --dry-run    # review distribution
python add_intent_to_v1.py              # writes to training_data/v2/

# Generate new examples
python generate_s1_v2_training.py --seed 42

# Merge into final dataset
python merge_v2_dataset.py
```

### Step 3: Train

Open `02_training/train_sft_v3.ipynb` and run all cells. The notebook:
1. Loads the previous LoRA checkpoint
2. Trains on the merged dataset (lr=5e-5, 3 epochs)
3. Tests intent classification on 4 test cases
4. Tests the 9 v0.4 benchmark failures
5. Saves LoRA adapter
6. Exports to GGUF (named `acervo-extractor-v2-Q4_K_M.gguf`)

### Step 4: Evaluate

```bash
cd 03_eval
python eval_benchmarks.py --model-path ../02_training/outputs/s1_sft_v3/final_lora \
    --benchmark-file ../01_dataset/benchmark_failures.jsonl
python eval_extraction.py --model-path ../02_training/outputs/s1_sft_v3/final_lora
```

### Step 5: Upload to HuggingFace

```bash
# Update REPO_ID in hf_upload/prepare_and_upload.py for new version
python hf_upload/prepare_and_upload.py --upload --include-gguf
```

## Schema

### Entity types
`person` `organization` `project` `technology` `place` `event` `document` `concept`

### Relation types
`part_of` `created_by` `maintains` `works_at` `member_of` `uses_technology` `depends_on` `alternative_to` `located_in` `deployed_on` `produces` `serves` `documented_in` `participated_in` `triggered_by` `resulted_in`

### Intent types (v2)
`overview` `specific` `chat` `followup`

### Retrieval modes (v2)
`summary_only` `with_chunks`

### Layers
- **PERSONAL** — user owns, created, or directly uses it
- **UNIVERSAL** — public knowledge (technologies, cities, fictional characters)

## Hardware

| Component | Spec |
|-----------|------|
| GPU | NVIDIA RTX 5070 Ti (16GB VRAM, Blackwell sm_120) |
| CUDA | 12.8 (cu128) |
| PyTorch | 2.10.0+cu128 |
| OS | Windows 11 |

## Using the model

### With LM Studio / Ollama

Download the GGUF from the [HF repo](https://huggingface.co/SandyVeliz/acervo-extractor-v2). Shows as **acervo-extractor-v2** in LM Studio.

### With Unsloth

```python
from unsloth import FastLanguageModel

model, tokenizer = FastLanguageModel.from_pretrained(
    "SandyVeliz/acervo-extractor-v2",
    max_seq_length=2048, load_in_4bit=True,
)
FastLanguageModel.for_inference(model)
```

### With Acervo

```python
from acervo import Acervo, OpenAIClient

llm = OpenAIClient(base_url="http://localhost:1234/v1", model="acervo-extractor-v2")
memory = Acervo(llm=llm, owner="user")
```

## License

Apache 2.0
