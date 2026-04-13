from __future__ import annotations

import re


EXPECTED_SECTIONS = {
    "intake": [
        "patient summary",
        "reported vitals",
        "key symptoms",
        "symptom timeline",
        "relevant medical history",
        "medication and allergy notes",
        "missing or unclear information",
    ],
    "triage": [
        "urgency level",
        "red-flag findings",
        "why this risk level fits",
        "recommended care setting",
        "immediate next actions",
        "information still needed for safer triage",
    ],
    "diagnosis": [
        "most likely condition categories",
        "top differential diagnoses",
        "supporting evidence",
        "conflicting or missing evidence",
        "suggested tests or clinical evaluations to confirm or rule out causes",
        "diagnostic uncertainty notes",
    ],
    "treatment": [
        "safety notice",
        "case summary",
        "urgency assessment",
        "possible disease categories and likely causes",
        "why these causes fit the case",
        "reasonable treatment pathways or management approaches",
        "what the patient should do next",
        "when to seek urgent or emergency care",
    ],
}

URGENCY_LEVELS = [
    "emergency now",
    "urgent same-day evaluation",
    "routine medical follow-up",
    "self-care with monitoring",
]


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def section_coverage(text: str, agent_name: str) -> float:
    normalized = normalize_whitespace(text)
    expected = EXPECTED_SECTIONS[agent_name]
    matched = sum(1 for section in expected if section in normalized)
    return matched / len(expected) if expected else 0.0


def parse_esi_label(text: str) -> int | None:
    match = re.search(r"\besi(?:\s*level)?\s*[-:]?\s*([1-5])\b", text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


def map_esi_to_urgency_bucket(esi: int | None) -> str | None:
    if esi == 1:
        return "emergency now"
    if esi in (2, 3):
        return "urgent same-day evaluation"
    if esi == 4:
        return "routine medical follow-up"
    if esi == 5:
        return "self-care with monitoring"
    return None


def parse_predicted_urgency(text: str) -> str | None:
    normalized = normalize_whitespace(text)
    for label in URGENCY_LEVELS:
        if label in normalized:
            return label
    return map_esi_to_urgency_bucket(parse_esi_label(text))


def missing_info_recall(intake_output: str, patient_case: dict) -> float:
    missing_fields = [name for name, value in patient_case.items() if normalize_whitespace(str(value)) == "not provided"]
    if not missing_fields:
        return 1.0

    normalized_output = normalize_whitespace(intake_output)
    hits = sum(1 for _ in missing_fields if "not provided" in normalized_output)
    return hits / len(missing_fields)


def compute_macro_f1(labels_true: list[str], labels_pred: list[str]) -> float:
    scores = []
    for label in URGENCY_LEVELS:
        tp = sum(1 for gold, pred in zip(labels_true, labels_pred) if gold == label and pred == label)
        fp = sum(1 for gold, pred in zip(labels_true, labels_pred) if gold != label and pred == label)
        fn = sum(1 for gold, pred in zip(labels_true, labels_pred) if gold == label and pred != label)
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        scores.append(0.0 if precision + recall == 0 else (2 * precision * recall / (precision + recall)))
    return sum(scores) / len(scores)


def average(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0
