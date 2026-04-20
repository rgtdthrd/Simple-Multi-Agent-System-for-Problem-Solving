from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


DIAGNOSIS_PATTERNS = [
    r"most likely diagnosis",
    r"most likely cause",
    r"most likely explanation",
    r"which of the following is the most likely",
    r"most likely underlying",
    r"most likely pathogen",
    r"most likely organism",
]

EXCLUDE_QUESTION_PATTERNS = [
    r"most appropriate treatment",
    r"best next step",
    r"correct next action",
    r"most appropriate next step",
    r"most appropriate management",
    r"next best diagnostic step",
    r"next best step in the workup",
    r"inciting factor",
    r"which of the following actions",
    r"which of the following is the correct next action",
    r"which of the following is the next best",
    r"expected beneficial effect",
    r"most appropriate treatment",
    r"mechanism of action",
    r"beneficial effect",
    r"pharmacokinetics",
    r"enzyme",
    r"receptor",
    r"pathway",
    r"histology",
    r"microscopy",
    r"chromosome",
    r"biochemistry",
    r"ethics committee",
    r"operative report",
]

EXCLUDE_ANSWER_PATTERNS = [
    r"\bmg\b",
    r"\bmcg\b",
    r"\beye drops\b",
    r"\bointment\b",
    r"\btherapy\b",
    r"\btreatment\b",
    r"\bsurgery\b",
    r"\bbiopsy\b",
    r"\bdisclose\b",
    r"\breport\b",
    r"\binhibition\b",
    r"\bcross-linking\b",
    r"\bgeneration of\b",
    r"^increased ",
    r"^decreased ",
    r"\bantibodies\b",
    r"\bresistance\b",
    r"\bregurgitation\b",
    r"\bpressure\b",
    r"\bfraction\b",
    r"\bmutation\b",
    r"\bflow cytometry\b",
    r"\btest\b",
]

SYMPTOM_PATTERNS = [
    r"pain",
    r"fever",
    r"cough",
    r"dyspnea",
    r"shortness of breath",
    r"nausea",
    r"vomiting",
    r"diarrhea",
    r"fatigue",
    r"weakness",
    r"headache",
    r"rash",
    r"syncope",
    r"wheezing",
    r"chest pain",
]

VITAL_PATTERNS = [
    r"temperature",
    r"temp",
    r"pulse",
    r"respirations",
    r"blood pressure",
    r"heart rate",
    r"\bbp\b",
    r"\bhr\b",
    r"platelet",
    r"creatinine",
    r"leukocyte",
    r"hemoglobin",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Select diagnosis-friendly MedQA cases for evaluation.")
    parser.add_argument("--input", required=True, help="Path to MedQA JSONL")
    parser.add_argument("--output", required=True, help="Path to selected JSONL")
    parser.add_argument("--count", type=int, default=100, help="Number of cases to select")
    return parser.parse_args()


def matches_any(text: str, patterns: list[str]) -> bool:
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)


def score_row(row: dict) -> tuple[int, list[str]]:
    question = str(row.get("question", ""))
    answer = str(row.get("answer", ""))
    reasons: list[str] = []
    score = 0

    if re.search(r"\b\d{1,3}-year-old\b", question, re.IGNORECASE):
        score += 3
        reasons.append("has_age")
    if matches_any(question, DIAGNOSIS_PATTERNS):
        score += 3
        reasons.append("diagnosis_style")
    if matches_any(question, SYMPTOM_PATTERNS):
        score += 2
        reasons.append("symptom_rich")
    if matches_any(question, VITAL_PATTERNS):
        score += 2
        reasons.append("has_vitals_or_labs")
    if "history" in question.lower():
        score += 1
        reasons.append("has_history")
    if len(question) >= 200:
        score += 1
        reasons.append("long_case")

    if matches_any(question, EXCLUDE_QUESTION_PATTERNS):
        score -= 4
        reasons.append("excluded_question_pattern")
    if matches_any(answer, EXCLUDE_ANSWER_PATTERNS):
        score -= 4
        reasons.append("excluded_answer_pattern")

    return score, reasons


def is_eligible(row: dict) -> bool:
    question = str(row.get("question", ""))
    answer = str(row.get("answer", ""))
    if not question or not answer or not row.get("options") or not row.get("answer_idx"):
        return False
    if not re.search(r"\b\d{1,3}-year-old\b", question, re.IGNORECASE):
        return False
    if matches_any(question, EXCLUDE_QUESTION_PATTERNS):
        return False
    if matches_any(answer, EXCLUDE_ANSWER_PATTERNS):
        return False
    if not (matches_any(question, DIAGNOSIS_PATTERNS) or matches_any(question, SYMPTOM_PATTERNS)):
        return False
    return True


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows = [json.loads(line) for line in input_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    candidates = []
    for idx, row in enumerate(rows, start=1):
        if not is_eligible(row):
            continue
        score, reasons = score_row(row)
        row["_selection_score"] = score
        row["_selection_reasons"] = reasons
        row["_source_index"] = idx
        candidates.append(row)

    candidates.sort(
        key=lambda row: (
            row["_selection_score"],
            len(str(row.get("question", ""))),
        ),
        reverse=True,
    )

    selected = candidates[: args.count]
    output_path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in selected) + ("\n" if selected else ""),
        encoding="utf-8",
    )

    print(f"Selected {len(selected)} cases from {len(rows)} rows")
    print(f"Wrote selection to {output_path}")


if __name__ == "__main__":
    main()
