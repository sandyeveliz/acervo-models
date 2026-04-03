# S1 Extraction Training Data

Training data for fine-tuning the Acervo S1 Unified extractor model.

## Files

- `s1_extraction.jsonl` — Training set (450 examples)
- `s1_validation.jsonl` — Validation set (50 examples)

## Format

Each line is a JSON object with `messages` array (system, user, assistant) in trl chat format.

- **System**: Fixed extraction prompt
- **User**: Existing graph nodes + topic hint + conversation turn
- **Assistant**: JSON with `{topic, entities, relations, facts}`

## Distribution

### By conversation type
| Type | Count |
|------|-------|
| First message / empty graph | 40 |
| Same topic, new facts | 80 |
| Same topic, new entities | 60 |
| Subtopic shift | 50 |
| Topic change | 50 |
| Query / question | 50 |
| Small talk / meta | 30 |
| Dedup / existing reference | 40 |
| Correction / update | 30 |
| Event extraction | 40 |
| File/document indexing | 30 |

### By domain
- Software development: ~35%
- Business / work: ~20%
- Literature / media: ~15%
- Personal: ~15%
- Academic / learning: ~15%

### Languages
~65% English, ~35% Spanish or mixed

## Generation

```bash
python 01_dataset/generate_s1_training.py --seed 42 --train 500 --val 50
```

Re-run with different `--seed` for varied output.
