from __future__ import annotations

import argparse
import json
from pathlib import Path

from .metrics import aggregate_group


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Aggregate evaluation case results and rank combinations.")
    parser.add_argument("--input", required=True, help="Path to case_results.jsonl")
    parser.add_argument("--weights", required=True, help="Path to scoring_weights.json")
    parser.add_argument("--output", default=None, help="Optional output JSON path")
    return parser.parse_args()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def compute_composite_score(summary: dict, weights: dict) -> float:
    score = 0.0
    for key, weight in weights.items():
        if key == "undertriage_penalty":
            score += weight * summary.get("undertriage_rate", 0.0)
        elif key == "latency_penalty_per_second":
            score += weight * summary.get("average_agent_latency", 0.0)
        else:
            score += weight * summary.get(key, 0.0)
    return score


def main() -> None:
    args = parse_args()
    rows = load_jsonl(Path(args.input))
    weights = load_json(Path(args.weights))

    grouped: dict[tuple[str, str], list[dict]] = {}
    for row in rows:
        key = (row["model_profile"], row["prompt_set"])
        grouped.setdefault(key, []).append(row)

    summaries = []
    for (model_profile, prompt_set), group_rows in grouped.items():
        summary = aggregate_group(group_rows)
        summary["model_profile"] = model_profile
        summary["prompt_set"] = prompt_set
        summary["composite_score"] = compute_composite_score(summary, weights)
        summaries.append(summary)

    summaries.sort(key=lambda item: item["composite_score"], reverse=True)
    result = {
        "best_combination": summaries[0] if summaries else None,
        "all_combinations": summaries,
    }

    if args.output:
        Path(args.output).write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
