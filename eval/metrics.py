from __future__ import annotations

from .parsers import (
    average,
    compute_macro_f1,
    missing_info_recall,
    parse_predicted_urgency,
    section_coverage,
)


def score_case_result(case_row: dict) -> dict:
    predicted_urgency = parse_predicted_urgency(case_row["triage_output"])
    gold_urgency = case_row["gold_urgency_bucket"]

    order = {
        "emergency now": 0,
        "urgent same-day evaluation": 1,
        "routine medical follow-up": 2,
        "self-care with monitoring": 3,
    }

    urgency_accuracy = 1.0 if predicted_urgency == gold_urgency else 0.0
    undertriage = 0.0
    overtriage = 0.0
    if predicted_urgency is not None:
        if order[predicted_urgency] > order[gold_urgency]:
            undertriage = 1.0
        elif order[predicted_urgency] < order[gold_urgency]:
            overtriage = 1.0

    return {
        "predicted_urgency": predicted_urgency,
        "urgency_accuracy": urgency_accuracy,
        "emergency_case": 1.0 if gold_urgency == "emergency now" else 0.0,
        "emergency_recall_hit": 1.0 if gold_urgency == "emergency now" and predicted_urgency == gold_urgency else 0.0,
        "undertriage": undertriage,
        "overtriage": overtriage,
        "intake_section_coverage": section_coverage(case_row["intake_output"], "intake"),
        "intake_missing_info_recall": missing_info_recall(case_row["intake_output"], case_row["patient_case"]),
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
    labels_true = [row["gold_urgency_bucket"] for row in rows]
    labels_pred = [row.get("predicted_urgency") or "self-care with monitoring" for row in rows]
    emergency_rows = [row for row in rows if row["gold_urgency_bucket"] == "emergency now"]

    summary = {
        "num_cases": len(rows),
        "urgency_accuracy": average([row["urgency_accuracy"] for row in rows]),
        "urgency_macro_f1": compute_macro_f1(labels_true, labels_pred),
        "undertriage_rate": average([row["undertriage"] for row in rows]),
        "overtriage_rate": average([row["overtriage"] for row in rows]),
        "intake_section_coverage": average([row["intake_section_coverage"] for row in rows]),
        "intake_missing_info_recall": average([row["intake_missing_info_recall"] for row in rows]),
        "triage_section_coverage": average([row["triage_section_coverage"] for row in rows]),
        "diagnosis_section_coverage": average([row["diagnosis_section_coverage"] for row in rows]),
        "treatment_section_coverage": average([row["treatment_section_coverage"] for row in rows]),
        "final_report_section_coverage": average([row["final_report_section_coverage"] for row in rows]),
        "average_agent_latency": average([row["average_agent_latency"] for row in rows]),
        "emergency_recall": (
            sum(row["emergency_recall_hit"] for row in emergency_rows) / len(emergency_rows)
            if emergency_rows
            else 0.0
        ),
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
