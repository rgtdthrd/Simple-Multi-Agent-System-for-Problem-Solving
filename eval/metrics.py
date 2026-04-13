from __future__ import annotations

from .parsers import average, best_option_by_similarity, parse_option_mentions, section_coverage


def score_case_result(case_row: dict) -> dict:
    options = case_row.get("options", {})
    gold_answer_idx = case_row.get("gold_answer_idx")
    gold_answer_text = case_row.get("gold_answer_text", "")

    diagnosis_ranked = parse_option_mentions(case_row["diagnosis_output"], options)
    treatment_ranked = parse_option_mentions(case_row["treatment_output"], options)

    ranked_predictions = []
    for option_key in diagnosis_ranked + treatment_ranked:
        if option_key not in ranked_predictions:
            ranked_predictions.append(option_key)

    if not ranked_predictions and options:
        fallback = best_option_by_similarity(case_row["diagnosis_output"], options)
        if fallback:
            ranked_predictions.append(fallback)

    predicted_top1 = ranked_predictions[0] if ranked_predictions else None

    return {
        "predicted_option_rankings": ranked_predictions,
        "predicted_top1_option": predicted_top1,
        "diagnosis_top1_accuracy": 1.0 if predicted_top1 == gold_answer_idx else 0.0,
        "diagnosis_top3_accuracy": 1.0 if gold_answer_idx in ranked_predictions[:3] else 0.0,
        "diagnosis_contains_gold_answer": (
            1.0 if gold_answer_text and gold_answer_text.lower() in case_row["diagnosis_output"].lower() else 0.0
        ),
        "intake_section_coverage": section_coverage(case_row["intake_output"], "intake"),
        "triage_section_coverage": section_coverage(case_row["triage_output"], "triage"),
        "diagnosis_section_coverage": section_coverage(case_row["diagnosis_output"], "diagnosis"),
        "treatment_section_coverage": section_coverage(case_row["treatment_output"], "treatment"),
        "final_report_section_coverage": section_coverage(case_row["treatment_output"], "treatment"),
        "average_agent_latency": average(
            [
                case_row.get("intake_duration_seconds") or 0.0,
                case_row.get("triage_duration_seconds") or 0.0,
                case_row.get("diagnosis_duration_seconds") or 0.0,
                case_row.get("treatment_duration_seconds") or 0.0,
            ]
        ),
    }


def aggregate_group(rows: list[dict]) -> dict:
    summary = {
        "num_cases": len(rows),
        "diagnosis_top1_accuracy": average([row["diagnosis_top1_accuracy"] for row in rows]),
        "diagnosis_top3_accuracy": average([row["diagnosis_top3_accuracy"] for row in rows]),
        "diagnosis_contains_gold_answer": average([row["diagnosis_contains_gold_answer"] for row in rows]),
        "intake_section_coverage": average([row["intake_section_coverage"] for row in rows]),
        "triage_section_coverage": average([row["triage_section_coverage"] for row in rows]),
        "diagnosis_section_coverage": average([row["diagnosis_section_coverage"] for row in rows]),
        "treatment_section_coverage": average([row["treatment_section_coverage"] for row in rows]),
        "final_report_section_coverage": average([row["final_report_section_coverage"] for row in rows]),
        "average_agent_latency": average([row["average_agent_latency"] for row in rows]),
    }

    judge_keys = [
        "judge_intake_grounding_score",
        "judge_triage_safety_score",
        "judge_diagnosis_plausibility_score",
        "judge_diagnosis_grounding_score",
        "judge_treatment_safety_score",
        "judge_treatment_actionability_score",
        "judge_overall_report_quality_score",
    ]
    for key in judge_keys:
        values = [row[key] for row in rows if row.get(key) is not None]
        if values:
            summary[key] = average(values)

    return summary
