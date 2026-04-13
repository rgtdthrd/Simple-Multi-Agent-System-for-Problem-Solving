from __future__ import annotations

import argparse
import json
from pathlib import Path

from openai import OpenAI

from src.medical_triage_system.coordinator import load_settings


JUDGE_PROMPT = """
You are evaluating outputs from a medical triage multi-agent system.
Score each category from 1 to 5, where 5 is best.
Return strict JSON with these integer fields only:
- judge_intake_grounding_score
- judge_triage_safety_score
- judge_diagnosis_plausibility_score
- judge_diagnosis_grounding_score
- judge_treatment_safety_score
- judge_treatment_actionability_score
- judge_overall_report_quality_score

Case:
{case_payload}
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run LLM-as-a-judge on case results.")
    parser.add_argument("--input", required=True, help="Path to case_results.jsonl")
    parser.add_argument("--output", required=True, help="Path to judged_case_results.jsonl")
    parser.add_argument("--model", default="gpt-4.1-mini", help="Judge model")
    return parser.parse_args()


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def save_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + ("\n" if rows else ""),
        encoding="utf-8",
    )


def main() -> None:
    args = parse_args()
    settings = load_settings()
    client = OpenAI(
        api_key=settings.OPENAI_API_KEY,
        base_url=getattr(settings, "OPENAI_BASE_URL", None),
    )
    rows = load_jsonl(Path(args.input))
    scored_rows = []

    for row in rows:
        case_payload = json.dumps(
            {
                "gold_urgency_bucket": row["gold_urgency_bucket"],
                "input_text": row["input_text"],
                "intake_output": row["intake_output"],
                "triage_output": row["triage_output"],
                "diagnosis_output": row["diagnosis_output"],
                "treatment_output": row["treatment_output"],
            },
            ensure_ascii=False,
        )
        response = client.responses.create(
            model=args.model,
            input=JUDGE_PROMPT.format(case_payload=case_payload),
        )
        try:
            judge_scores = json.loads(response.output_text.strip())
        except json.JSONDecodeError:
            judge_scores = {}
        row.update(judge_scores)
        scored_rows.append(row)

    save_jsonl(Path(args.output), scored_rows)
    print(f"Saved judged rows to {args.output}")


if __name__ == "__main__":
    main()
