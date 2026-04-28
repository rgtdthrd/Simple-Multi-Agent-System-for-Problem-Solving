from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from .aggregate_results import compute_composite_score, load_json, load_jsonl
from .metrics import aggregate_group


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plot evaluation metrics from benchmark case results.")
    parser.add_argument("--input", required=True, help="Path to case_results.jsonl")
    parser.add_argument("--weights", required=True, help="Path to scoring_weights.json")
    parser.add_argument("--output-dir", default=None, help="Optional output directory")
    return parser.parse_args()


def build_summary_frame(rows: list[dict], weights: dict) -> pd.DataFrame:
    grouped: dict[tuple[str, str], list[dict]] = {}
    for row in rows:
        grouped.setdefault((row["model_profile"], row["prompt_set"]), []).append(row)

    summaries: list[dict] = []
    for (model_profile, prompt_set), group_rows in grouped.items():
        summary = aggregate_group(group_rows)
        summary["model_profile"] = model_profile
        summary["prompt_set"] = prompt_set
        summary["label"] = f"{model_profile}\n{prompt_set}"
        summary["composite_score"] = compute_composite_score(summary, weights)
        summaries.append(summary)

    df = pd.DataFrame(summaries)
    return df.sort_values(by="composite_score", ascending=False).reset_index(drop=True)


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    weights_path = Path(args.weights)
    output_dir = Path(args.output_dir) if args.output_dir else input_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    rows = load_jsonl(input_path)
    weights = load_json(weights_path)
    summary_df = build_summary_frame(rows, weights)
    summary_csv_path = output_dir / "metrics_summary.csv"
    figure_path = output_dir / "metrics_overview.png"

    summary_df.to_csv(summary_csv_path, index=False)

    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))

    sns.barplot(data=summary_df, x="label", y="diagnosis_top1_accuracy", ax=axes[0, 0], palette="Blues_d")
    axes[0, 0].set_title("Diagnosis Top-1 Accuracy")
    axes[0, 0].set_xlabel("")
    axes[0, 0].set_ylabel("Score")
    axes[0, 0].tick_params(axis="x", rotation=0)

    sns.barplot(data=summary_df, x="label", y="diagnosis_top3_accuracy", ax=axes[0, 1], palette="Greens_d")
    axes[0, 1].set_title("Diagnosis Top-3 Accuracy")
    axes[0, 1].set_xlabel("")
    axes[0, 1].set_ylabel("Score")
    axes[0, 1].tick_params(axis="x", rotation=0)

    sns.barplot(data=summary_df, x="label", y="average_agent_latency", ax=axes[1, 0], palette="Oranges_d")
    axes[1, 0].set_title("Average Agent Latency")
    axes[1, 0].set_xlabel("")
    axes[1, 0].set_ylabel("Seconds")
    axes[1, 0].tick_params(axis="x", rotation=0)

    sns.barplot(data=summary_df, x="label", y="composite_score", ax=axes[1, 1], palette="Purples_d")
    axes[1, 1].set_title("Composite Score")
    axes[1, 1].set_xlabel("")
    axes[1, 1].set_ylabel("Score")
    axes[1, 1].tick_params(axis="x", rotation=0)

    fig.suptitle("Evaluation Metrics Overview", fontsize=16, y=0.98)
    plt.tight_layout()
    fig.savefig(figure_path, dpi=200, bbox_inches="tight")
    plt.close(fig)

    print(f"Saved metrics summary CSV to {summary_csv_path}")
    print(f"Saved metrics figure to {figure_path}")


if __name__ == "__main__":
    main()
