#!/usr/bin/env python3
"""
Evaluate the S1 model against the benchmark suite.

Runs inference on the benchmark turns and computes per-field accuracy metrics.
Can compare v1 vs v2 models if both result files exist.

Usage:
    python 03_eval/eval_benchmarks.py --model-path <path_to_lora> [--base-model unsloth/Qwen3.5-9B]
    python 03_eval/eval_benchmarks.py --compare eval_v1_baseline.json eval_v2.json
"""

import json
import argparse
import sys
from pathlib import Path
from collections import Counter
from difflib import SequenceMatcher

EVAL_DIR = Path("03_eval")
FAILURES_PATH = Path("01_dataset/benchmark_failures.jsonl")


# ═══════════════════════════════════════════════════════════════════════════
# Scoring Functions
# ═══════════════════════════════════════════════════════════════════════════

def parse_output(raw: str) -> dict | None:
    """Parse model output JSON. Returns None on failure."""
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Try to extract JSON from markdown code blocks
        if "```" in raw:
            start = raw.find("{")
            end = raw.rfind("}") + 1
            if start >= 0 and end > start:
                try:
                    return json.loads(raw[start:end])
                except json.JSONDecodeError:
                    pass
        return None


def score_intent(predicted: dict, expected: dict) -> dict:
    """Score intent classification."""
    pred = predicted.get("intent", "")
    exp = expected.get("intent", "")
    return {
        "correct": pred == exp,
        "predicted": pred,
        "expected": exp,
    }


def score_topic(predicted: dict, expected: dict) -> dict:
    """Score topic classification."""
    pred_action = predicted.get("topic", {}).get("action", "")
    exp_action = expected.get("topic", {}).get("action", "")
    action_match = pred_action == exp_action

    pred_label = predicted.get("topic", {}).get("label") or ""
    exp_label = expected.get("topic", {}).get("label") or ""
    label_sim = SequenceMatcher(None, pred_label.lower(), exp_label.lower()).ratio() if pred_label and exp_label else (1.0 if pred_label == exp_label else 0.0)

    return {
        "action_correct": action_match,
        "label_similarity": label_sim,
        "predicted_action": pred_action,
        "expected_action": exp_action,
    }


def score_retrieval(predicted: dict, expected: dict) -> dict:
    """Score retrieval decision."""
    pred = predicted.get("retrieval", "")
    exp = expected.get("retrieval", "")
    return {
        "correct": pred == exp,
        "predicted": pred,
        "expected": exp,
    }


def score_entities(predicted: dict, expected: dict) -> dict:
    """Score entity extraction via ID matching."""
    pred_ids = {e.get("id", "") for e in predicted.get("entities", [])}
    exp_ids = {e.get("id", "") for e in expected.get("entities", [])}

    if not exp_ids and not pred_ids:
        return {"precision": 1.0, "recall": 1.0, "f1": 1.0, "pred_count": 0, "exp_count": 0}

    tp = len(pred_ids & exp_ids)
    precision = tp / len(pred_ids) if pred_ids else 0.0
    recall = tp / len(exp_ids) if exp_ids else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    return {"precision": precision, "recall": recall, "f1": f1, "pred_count": len(pred_ids), "exp_count": len(exp_ids)}


def score_relations(predicted: dict, expected: dict) -> dict:
    """Score relation extraction."""
    def rel_key(r):
        return (r.get("source", ""), r.get("target", ""), r.get("relation", ""))

    pred_rels = {rel_key(r) for r in predicted.get("relations", [])}
    exp_rels = {rel_key(r) for r in expected.get("relations", [])}

    if not exp_rels and not pred_rels:
        return {"precision": 1.0, "recall": 1.0, "f1": 1.0}

    tp = len(pred_rels & exp_rels)
    precision = tp / len(pred_rels) if pred_rels else 0.0
    recall = tp / len(exp_rels) if exp_rels else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    return {"precision": precision, "recall": recall, "f1": f1}


def score_facts(predicted: dict, expected: dict) -> dict:
    """Score fact extraction via fuzzy text match."""
    pred_facts = [(f.get("entity", ""), f.get("text", "")) for f in predicted.get("facts", [])]
    exp_facts = [(f.get("entity", ""), f.get("text", "")) for f in expected.get("facts", [])]

    if not exp_facts and not pred_facts:
        return {"recall": 1.0, "pred_count": 0, "exp_count": 0}

    matched = 0
    for exp_ent, exp_text in exp_facts:
        for pred_ent, pred_text in pred_facts:
            if exp_ent == pred_ent:
                sim = SequenceMatcher(None, pred_text.lower(), exp_text.lower()).ratio()
                if sim > 0.6:
                    matched += 1
                    break

    recall = matched / len(exp_facts) if exp_facts else 0.0
    return {"recall": recall, "pred_count": len(pred_facts), "exp_count": len(exp_facts)}


def score_turn(predicted: dict, expected: dict) -> dict:
    """Score a complete turn."""
    return {
        "intent": score_intent(predicted, expected),
        "topic": score_topic(predicted, expected),
        "retrieval": score_retrieval(predicted, expected),
        "entities": score_entities(predicted, expected),
        "relations": score_relations(predicted, expected),
        "facts": score_facts(predicted, expected),
    }


# ═══════════════════════════════════════════════════════════════════════════
# Benchmark Runner
# ═══════════════════════════════════════════════════════════════════════════

def load_benchmark_turns(path: Path) -> list[dict]:
    """Load benchmark turns from JSONL file."""
    turns = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                turns.append(json.loads(line))
    return turns


def run_inference_unsloth(model_path: str, base_model: str, turns: list[dict]) -> list[str]:
    """Run inference using unsloth/transformers."""
    try:
        from unsloth import FastLanguageModel
    except ImportError:
        print("ERROR: unsloth not installed. Install with: pip install unsloth")
        sys.exit(1)

    print(f"Loading model from {model_path}...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model_path,
        max_seq_length=2048,
        load_in_4bit=True,
    )
    FastLanguageModel.for_inference(model)

    results = []
    for i, turn in enumerate(turns):
        messages = [
            {"role": "system", "content": turn["messages"][0]["content"]},
            {"role": "user", "content": turn["messages"][1]["content"]},
        ]

        inputs = tokenizer.apply_chat_template(
            messages, tokenize=True, add_generation_prompt=True, return_tensors="pt"
        ).to(model.device)

        outputs = model.generate(
            input_ids=inputs,
            max_new_tokens=1024,
            temperature=0.1,
            do_sample=False,
        )

        response = tokenizer.decode(outputs[0][inputs.shape[-1]:], skip_special_tokens=True)
        results.append(response.strip())

        if (i + 1) % 10 == 0:
            print(f"  Processed {i+1}/{len(turns)} turns")

    return results


def evaluate(turns: list[dict], predictions: list[str]) -> dict:
    """Evaluate predictions against expected outputs."""
    results = {
        "total": len(turns),
        "json_parse_ok": 0,
        "scores": [],
        "failures": [],
    }

    for i, (turn, pred_raw) in enumerate(zip(turns, predictions)):
        expected = json.loads(turn["messages"][2]["content"])
        predicted = parse_output(pred_raw)

        if predicted is None:
            results["failures"].append({
                "turn": i,
                "error": "JSON parse failure",
                "raw": pred_raw[:200],
            })
            continue

        results["json_parse_ok"] += 1
        turn_score = score_turn(predicted, expected)
        turn_score["turn_index"] = i

        # Extract user message for context
        user_content = turn["messages"][1]["content"]
        user_msg_match = user_content.split("USER: ")[-1] if "USER: " in user_content else user_content[:80]
        turn_score["user_message"] = user_msg_match[:80]

        results["scores"].append(turn_score)

    # Aggregate
    total_scored = len(results["scores"])
    if total_scored > 0:
        results["aggregate"] = {
            "json_parse_rate": results["json_parse_ok"] / results["total"],
            "intent_accuracy": sum(1 for s in results["scores"] if s["intent"]["correct"]) / total_scored,
            "topic_action_accuracy": sum(1 for s in results["scores"] if s["topic"]["action_correct"]) / total_scored,
            "retrieval_accuracy": sum(1 for s in results["scores"] if s["retrieval"]["correct"]) / total_scored,
            "entity_f1": sum(s["entities"]["f1"] for s in results["scores"]) / total_scored,
            "relation_f1": sum(s["relations"]["f1"] for s in results["scores"]) / total_scored,
            "fact_recall": sum(s["facts"]["recall"] for s in results["scores"]) / total_scored,
        }
    else:
        results["aggregate"] = {}

    return results


def print_results(results: dict, label: str = ""):
    """Print evaluation results."""
    print(f"\n{'=' * 60}")
    if label:
        print(f"  {label}")
        print(f"{'=' * 60}")

    agg = results.get("aggregate", {})
    if not agg:
        print("  No results to display.")
        return

    print(f"\n  {'Metric':<30s} {'Score':>10s}")
    print(f"  {'-'*30} {'-'*10}")
    print(f"  {'JSON parse rate':<30s} {agg['json_parse_rate']:>9.1%}")
    print(f"  {'Intent accuracy':<30s} {agg['intent_accuracy']:>9.1%}")
    print(f"  {'Topic action accuracy':<30s} {agg['topic_action_accuracy']:>9.1%}")
    print(f"  {'Retrieval accuracy':<30s} {agg['retrieval_accuracy']:>9.1%}")
    print(f"  {'Entity F1':<30s} {agg['entity_f1']:>9.1%}")
    print(f"  {'Relation F1':<30s} {agg['relation_f1']:>9.1%}")
    print(f"  {'Fact recall':<30s} {agg['fact_recall']:>9.1%}")

    # Intent confusion
    print(f"\n  Intent breakdown:")
    intent_results = Counter()
    for s in results["scores"]:
        key = f"{s['intent']['expected']} → {s['intent']['predicted']}"
        intent_results[key] += 1
    for key, count in sorted(intent_results.items()):
        marker = " ✗" if key.split(" → ")[0] != key.split(" → ")[1] else ""
        print(f"    {key}: {count}{marker}")

    # Failures
    if results["failures"]:
        print(f"\n  Parse failures: {len(results['failures'])}")
        for f in results["failures"][:5]:
            print(f"    Turn {f['turn']}: {f['error']}")


def compare_results(v1_path: str, v2_path: str):
    """Compare two evaluation result files."""
    with open(v1_path) as f:
        v1 = json.load(f)
    with open(v2_path) as f:
        v2 = json.load(f)

    print(f"\n{'=' * 60}")
    print(f"  v1 vs v2 Comparison")
    print(f"{'=' * 60}")

    v1_agg = v1.get("aggregate", {})
    v2_agg = v2.get("aggregate", {})

    metrics = [
        ("JSON parse rate", "json_parse_rate"),
        ("Intent accuracy", "intent_accuracy"),
        ("Topic action accuracy", "topic_action_accuracy"),
        ("Retrieval accuracy", "retrieval_accuracy"),
        ("Entity F1", "entity_f1"),
        ("Relation F1", "relation_f1"),
        ("Fact recall", "fact_recall"),
    ]

    print(f"\n  {'Metric':<30s} {'v1':>8s} {'v2':>8s} {'Delta':>8s}")
    print(f"  {'-'*30} {'-'*8} {'-'*8} {'-'*8}")

    for label, key in metrics:
        v1_val = v1_agg.get(key, 0)
        v2_val = v2_agg.get(key, 0)
        delta = v2_val - v1_val
        delta_str = f"+{delta:.1%}" if delta >= 0 else f"{delta:.1%}"
        print(f"  {label:<30s} {v1_val:>7.1%} {v2_val:>7.1%} {delta_str:>8s}")


def eval_benchmark_failures(turns: list[dict], predictions: list[str]):
    """Specifically evaluate the 9 S1 failures from v0.4."""
    if not FAILURES_PATH.exists():
        print("\n  benchmark_failures.jsonl not found, skipping failure eval")
        return

    failures = load_benchmark_turns(FAILURES_PATH)
    print(f"\n{'=' * 60}")
    print(f"  v0.4 Failure Cases ({len(failures)} turns)")
    print(f"{'=' * 60}")

    # Run each failure through the model
    # (In practice, these would need to be part of the turns list)
    print("  Note: Run this separately with --benchmark-file 01_dataset/benchmark_failures.jsonl")


# ═══════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Evaluate S1 model on benchmark suite")
    parser.add_argument("--model-path", type=str, help="Path to LoRA adapter")
    parser.add_argument("--base-model", type=str, default="unsloth/Qwen3.5-9B", help="Base model name")
    parser.add_argument("--benchmark-file", type=str, default="01_dataset/benchmark_failures.jsonl",
                        help="JSONL file with benchmark turns")
    parser.add_argument("--output", type=str, default="03_eval/eval_results.json",
                        help="Output file for results")
    parser.add_argument("--compare", nargs=2, metavar=("V1", "V2"),
                        help="Compare two result files")
    parser.add_argument("--from-predictions", type=str,
                        help="Load predictions from file instead of running inference")
    args = parser.parse_args()

    if args.compare:
        compare_results(args.compare[0], args.compare[1])
        return

    # Load benchmark
    benchmark_path = Path(args.benchmark_file)
    if not benchmark_path.exists():
        print(f"ERROR: Benchmark file not found: {benchmark_path}")
        sys.exit(1)

    turns = load_benchmark_turns(benchmark_path)
    print(f"Loaded {len(turns)} benchmark turns from {benchmark_path}")

    if args.from_predictions:
        # Load pre-computed predictions
        with open(args.from_predictions) as f:
            predictions = [line.strip() for line in f]
    elif args.model_path:
        # Run inference
        predictions = run_inference_unsloth(args.model_path, args.base_model, turns)
    else:
        # Evaluate expected outputs against themselves (sanity check)
        print("No model specified — running sanity check (expected vs expected)")
        predictions = [t["messages"][2]["content"] for t in turns]

    # Evaluate
    results = evaluate(turns, predictions)
    print_results(results, label=args.model_path or "Sanity Check")

    # Save results
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {output_path}")


if __name__ == "__main__":
    main()
