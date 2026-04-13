from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass
class EvalCase:
    case_id: str
    source_dataset: str
    instruction: str
    input_text: str
    gold_output_text: str
    gold_esi: int | None
    gold_urgency_bucket: str
    patient_case: dict
    metadata: dict

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class CaseRunResult:
    case_id: str
    model_profile: str
    prompt_set: str
    gold_esi: int | None
    gold_urgency_bucket: str
    intake_output: str
    triage_output: str
    diagnosis_output: str
    treatment_output: str
    intake_duration_seconds: float | None
    triage_duration_seconds: float | None
    diagnosis_duration_seconds: float | None
    treatment_duration_seconds: float | None
    total_duration_seconds: float

    def to_dict(self) -> dict:
        return asdict(self)
