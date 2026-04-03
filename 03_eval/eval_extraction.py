#!/usr/bin/env python3
"""
Evaluate entity extraction quality on indexed content (code, prose, docs).

Creates a small eval set of 20 examples with known entities and measures
precision/recall in isolation (not the full pipeline).

Usage:
    python 03_eval/eval_extraction.py --model-path <path_to_lora>
    python 03_eval/eval_extraction.py --sanity-check
"""

import json
import argparse
import sys
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════
# Eval Set — 20 examples with known entities
# ═══════════════════════════════════════════════════════════════════════════

EVAL_SET = [
    # ── Code examples (8) ──
    {
        "category": "code",
        "input": "Here's the authentication setup:\n\n```typescript\nimport { createClient } from '@supabase/supabase-js';\nimport jwt from 'jsonwebtoken';\n\nexport const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);\n```",
        "expected_entity_ids": {"supabase", "jsonwebtoken"},
        "expected_entity_types": {"technology"},
    },
    {
        "category": "code",
        "input": "The API uses FastAPI with SQLAlchemy ORM:\n\n```python\nfrom fastapi import FastAPI\nfrom sqlalchemy.ext.asyncio import AsyncSession\nfrom redis import Redis\n\napp = FastAPI(title='Beacon API')\n```",
        "expected_entity_ids": {"fastapi", "sqlalchemy", "redis"},
        "expected_entity_types": {"technology"},
    },
    {
        "category": "code",
        "input": "Docker deployment config:\n\n```yaml\nservices:\n  web:\n    image: node:20\n    depends_on: [postgres, redis]\n  postgres:\n    image: postgres:16\n  redis:\n    image: redis:7\n```",
        "expected_entity_ids": {"docker", "postgresql", "redis"},
        "expected_entity_types": {"technology"},
    },
    {
        "category": "code",
        "input": "Just utility helpers, nothing special:\n\n```typescript\nexport const delay = (ms: number) => new Promise(r => setTimeout(r, ms));\nexport const capitalize = (s: string) => s[0].toUpperCase() + s.slice(1);\n```",
        "expected_entity_ids": set(),
        "expected_entity_types": set(),
    },
    {
        "category": "code",
        "input": "CI/CD pipeline configuration:\n\n```yaml\nname: Deploy\non: push\njobs:\n  build:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n      - run: npm ci && npm test && npm run build\n      - uses: docker/build-push-action@v5\n```",
        "expected_entity_ids": {"github_actions", "docker"},
        "expected_entity_types": {"technology"},
    },
    {
        "category": "code",
        "input": "The frontend uses React with TailwindCSS:\n\n```tsx\nimport { useState } from 'react';\nimport { Button } from '@/components/ui/button';\n\nexport function Counter() {\n  const [count, setCount] = useState(0);\n  return <Button onClick={() => setCount(c => c + 1)}>{count}</Button>;\n}\n```",
        "expected_entity_ids": {"react", "tailwind"},
        "expected_entity_types": {"technology"},
    },
    {
        "category": "code",
        "input": "Testing setup with Jest and Testing Library:\n\n```typescript\nimport { render, screen } from '@testing-library/react';\nimport { Dashboard } from './Dashboard';\n\ntest('renders dashboard title', () => {\n  render(<Dashboard />);\n  expect(screen.getByText('Dashboard')).toBeInTheDocument();\n});\n```",
        "expected_entity_ids": {"jest", "testing_library"},
        "expected_entity_types": {"technology"},
    },
    {
        "category": "code",
        "input": "Database migration for users table:\n\n```python\ndef upgrade():\n    op.add_column('users', sa.Column('avatar_url', sa.String(500)))\n    op.add_column('users', sa.Column('bio', sa.Text()))\n```",
        "expected_entity_ids": set(),
        "expected_entity_types": set(),
    },

    # ── Prose examples (6) ──
    {
        "category": "prose",
        "input": "Harry stared at the letter in his hand. Dumbledore had written it himself, the familiar looping handwriting unmistakable. Hermione leaned over his shoulder, reading along.",
        "expected_entity_ids": {"harry_potter", "dumbledore", "hermione_granger"},
        "expected_entity_types": {"person"},
    },
    {
        "category": "prose",
        "input": "Frodo and Sam reached the gates of Mordor after weeks of travel. Gollum led them through a hidden path, whispering about 'the precious' the entire way.",
        "expected_entity_ids": {"frodo", "samwise", "gollum", "mordor"},
        "expected_entity_types": {"person", "place"},
    },
    {
        "category": "prose",
        "input": "The sun cast long shadows across the desert. Not a sound could be heard for miles. The sand stretched endlessly in every direction.",
        "expected_entity_ids": set(),
        "expected_entity_types": set(),
    },
    {
        "category": "prose",
        "input": "Paul Atreides stood before the Fremen council on Arrakis. Stilgar vouched for him, and Chani watched from the shadows.",
        "expected_entity_ids": {"paul_atreides", "stilgar", "chani", "arrakis"},
        "expected_entity_types": {"person", "place"},
    },
    {
        "category": "prose",
        "input": "Luke ignited his lightsaber as Darth Vader approached. The corridor of the Death Star hummed with energy. 'I am your father,' Vader said.",
        "expected_entity_ids": {"luke_skywalker", "darth_vader", "death_star"},
        "expected_entity_types": {"person", "place"},
    },
    {
        "category": "prose",
        "input": "La lluvia caía sobre Buenos Aires. María caminaba por Florida, pensando en su conversación con Carlos. Él le había dicho que se mudaba a Mendoza.",
        "expected_entity_ids": {"buenos_aires", "mendoza"},
        "expected_entity_types": {"place", "person"},
    },

    # ── Documentation examples (6) ──
    {
        "category": "docs",
        "input": "# Project Beacon\n\nA real-time analytics dashboard built with React, FastAPI, and PostgreSQL.\nMaintained by Alice Chen and Bob Martinez.\nDeployed on AWS using Docker containers.",
        "expected_entity_ids": {"react", "fastapi", "postgresql", "aws", "docker"},
        "expected_entity_types": {"technology", "person"},
    },
    {
        "category": "docs",
        "input": "Sprint 12 completed:\n- FEAT-101: User authentication (Alice)\n- BUG-205: Fix dashboard crash (Bob)\n- TECH-301: Upgrade to React 19 (Priya)\n\nVelocity: 18 points",
        "expected_entity_ids": set(),
        "expected_entity_types": {"person", "event"},
    },
    {
        "category": "docs",
        "input": "## Changelog v3.0\n\n- Added GraphQL API alongside REST\n- Migrated from MySQL to PostgreSQL\n- New real-time WebSocket support\n- Breaking: Dropped Python 3.9 support",
        "expected_entity_ids": {"graphql", "mysql", "postgresql"},
        "expected_entity_types": {"technology"},
    },
    {
        "category": "docs",
        "input": "## Contributing\n\n1. Fork the repository\n2. Create a feature branch\n3. Run tests with `npm test`\n4. Submit a pull request",
        "expected_entity_ids": set(),
        "expected_entity_types": set(),
    },
    {
        "category": "docs",
        "input": "Architecture Decision: We chose Supabase over Firebase for these reasons:\n1. PostgreSQL gives us SQL flexibility\n2. Row Level Security for multi-tenancy\n3. Better self-hosting options\n4. Open source",
        "expected_entity_ids": {"supabase", "firebase", "postgresql"},
        "expected_entity_types": {"technology"},
    },
    {
        "category": "docs",
        "input": "Bug Report #1234\nTitle: Login fails with Google OAuth\nReporter: Alice Chen\nSeverity: Critical\nAffected version: 2.1.0\nSteps: 1. Click 'Sign in with Google' 2. Complete OAuth flow 3. Redirect fails with 500 error",
        "expected_entity_ids": set(),
        "expected_entity_types": {"person", "concept"},
    },
]


# ═══════════════════════════════════════════════════════════════════════════
# Scoring
# ═══════════════════════════════════════════════════════════════════════════

def score_extraction(predicted_output: dict, expected: dict) -> dict:
    """Score entity extraction for a single example."""
    pred_entities = predicted_output.get("entities", [])
    pred_ids = {e.get("id", "").lower() for e in pred_entities}
    pred_types = {e.get("type", "") for e in pred_entities}

    exp_ids = expected["expected_entity_ids"]
    exp_types = expected["expected_entity_types"]

    # ID-based scoring (flexible — check if expected IDs appear in predictions)
    if not exp_ids and not pred_ids:
        id_precision = 1.0
        id_recall = 1.0
    elif not exp_ids:
        id_precision = 0.0  # false positives
        id_recall = 1.0
    elif not pred_ids:
        id_precision = 1.0
        id_recall = 0.0
    else:
        # Fuzzy ID matching (allow partial matches)
        matched = 0
        for exp_id in exp_ids:
            for pred_id in pred_ids:
                if exp_id in pred_id or pred_id in exp_id:
                    matched += 1
                    break
        id_recall = matched / len(exp_ids)
        # Precision: how many predictions are relevant
        relevant = 0
        for pred_id in pred_ids:
            for exp_id in exp_ids:
                if exp_id in pred_id or pred_id in exp_id:
                    relevant += 1
                    break
        id_precision = relevant / len(pred_ids) if pred_ids else 0.0

    id_f1 = 2 * id_precision * id_recall / (id_precision + id_recall) if (id_precision + id_recall) > 0 else 0.0

    # Type coverage — did we produce the expected entity types?
    if exp_types:
        type_coverage = len(pred_types & exp_types) / len(exp_types)
    else:
        type_coverage = 1.0 if not pred_types else 0.0

    return {
        "category": expected["category"],
        "id_precision": id_precision,
        "id_recall": id_recall,
        "id_f1": id_f1,
        "type_coverage": type_coverage,
        "pred_count": len(pred_ids),
        "exp_count": len(exp_ids),
        "pred_ids": sorted(pred_ids),
        "exp_ids": sorted(exp_ids),
    }


def run_eval(predictions: list[dict]) -> dict:
    """Run evaluation on all examples."""
    results = {
        "total": len(EVAL_SET),
        "scores": [],
        "by_category": {},
    }

    for i, (example, pred) in enumerate(zip(EVAL_SET, predictions)):
        score = score_extraction(pred, example)
        score["index"] = i
        results["scores"].append(score)

    # Aggregate by category
    from collections import defaultdict
    by_cat = defaultdict(list)
    for s in results["scores"]:
        by_cat[s["category"]].append(s)

    for cat, scores in by_cat.items():
        n = len(scores)
        results["by_category"][cat] = {
            "count": n,
            "avg_precision": sum(s["id_precision"] for s in scores) / n,
            "avg_recall": sum(s["id_recall"] for s in scores) / n,
            "avg_f1": sum(s["id_f1"] for s in scores) / n,
            "avg_type_coverage": sum(s["type_coverage"] for s in scores) / n,
        }

    # Overall
    all_scores = results["scores"]
    n = len(all_scores)
    results["aggregate"] = {
        "avg_precision": sum(s["id_precision"] for s in all_scores) / n,
        "avg_recall": sum(s["id_recall"] for s in all_scores) / n,
        "avg_f1": sum(s["id_f1"] for s in all_scores) / n,
        "avg_type_coverage": sum(s["type_coverage"] for s in all_scores) / n,
    }

    return results


def print_eval_results(results: dict):
    """Print evaluation results."""
    print(f"\n{'=' * 60}")
    print(f"  Extraction Evaluation Results")
    print(f"{'=' * 60}")

    # By category
    print(f"\n  {'Category':<12s} {'P':>8s} {'R':>8s} {'F1':>8s} {'Type':>8s} {'N':>4s}")
    print(f"  {'-'*12} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*4}")
    for cat, stats in sorted(results["by_category"].items()):
        print(f"  {cat:<12s} {stats['avg_precision']:>7.1%} {stats['avg_recall']:>7.1%} "
              f"{stats['avg_f1']:>7.1%} {stats['avg_type_coverage']:>7.1%} {stats['count']:>4d}")

    # Overall
    agg = results["aggregate"]
    print(f"  {'OVERALL':<12s} {agg['avg_precision']:>7.1%} {agg['avg_recall']:>7.1%} "
          f"{agg['avg_f1']:>7.1%} {agg['avg_type_coverage']:>7.1%} {results['total']:>4d}")

    # Detail on misses
    print(f"\n  Misses (expected but not found):")
    for s in results["scores"]:
        if s["id_recall"] < 1.0 and s["exp_count"] > 0:
            missed = set(s["exp_ids"]) - set(s["pred_ids"])
            if missed:
                print(f"    [{s['category']}] #{s['index']}: missed {missed}")


def main():
    parser = argparse.ArgumentParser(description="Evaluate entity extraction on indexed content")
    parser.add_argument("--model-path", type=str, help="Path to LoRA adapter")
    parser.add_argument("--base-model", type=str, default="unsloth/Qwen3.5-9B")
    parser.add_argument("--sanity-check", action="store_true", help="Run with perfect predictions")
    parser.add_argument("--output", type=str, default="03_eval/eval_extraction_results.json")
    args = parser.parse_args()

    from schema import S1_SYSTEM_PROMPT

    if args.sanity_check:
        print("Running sanity check with expected outputs...")
        # Create "perfect" predictions matching expected
        predictions = []
        for ex in EVAL_SET:
            entities = []
            for eid in ex["expected_entity_ids"]:
                etype = list(ex["expected_entity_types"])[0] if ex["expected_entity_types"] else "concept"
                entities.append({"id": eid, "label": eid.replace("_", " ").title(), "type": etype, "layer": "UNIVERSAL"})
            predictions.append({"entities": entities})
        results = run_eval(predictions)
        print_eval_results(results)
        return

    if args.model_path:
        # Run actual inference
        try:
            from unsloth import FastLanguageModel
        except ImportError:
            print("ERROR: unsloth not installed")
            sys.exit(1)

        print(f"Loading model from {args.model_path}...")
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=args.model_path,
            max_seq_length=2048,
            load_in_4bit=True,
        )
        FastLanguageModel.for_inference(model)

        predictions = []
        for i, example in enumerate(EVAL_SET):
            messages = [
                {"role": "system", "content": S1_SYSTEM_PROMPT},
                {"role": "user", "content": f"EXISTING NODES:\n[]\n\nTOPIC HINT: unresolved — classify the topic yourself\nCURRENT TOPIC: null\n\nPREVIOUS ASSISTANT: null\nUSER: {example['input']}"},
            ]
            inputs = tokenizer.apply_chat_template(
                messages, tokenize=True, add_generation_prompt=True, return_tensors="pt"
            ).to(model.device)
            outputs = model.generate(input_ids=inputs, max_new_tokens=1024, temperature=0.1, do_sample=False)
            response = tokenizer.decode(outputs[0][inputs.shape[-1]:], skip_special_tokens=True).strip()

            try:
                pred = json.loads(response)
            except json.JSONDecodeError:
                pred = {"entities": []}

            predictions.append(pred)
            if (i + 1) % 5 == 0:
                print(f"  Processed {i+1}/{len(EVAL_SET)}")

        results = run_eval(predictions)
        print_eval_results(results)

        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {output_path}")
    else:
        print("Specify --model-path or --sanity-check")
        sys.exit(1)


if __name__ == "__main__":
    main()
