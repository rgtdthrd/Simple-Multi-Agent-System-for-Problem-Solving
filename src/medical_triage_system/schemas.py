from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass
class PatientCase:
    age: str
    sex: str
    vitals: str
    symptoms: str
    medical_history: str
    current_medications: str
    allergies: str
    duration: str

    def to_prompt_block(self) -> str:
        return (
            f"Age: {self.age}\n"
            f"Sex: {self.sex}\n"
            f"Vitals: {self.vitals}\n"
            f"Symptoms: {self.symptoms}\n"
            f"Duration: {self.duration}\n"
            f"Medical history: {self.medical_history}\n"
            f"Current medications: {self.current_medications}\n"
            f"Allergies: {self.allergies}"
        )


@dataclass
class AgentRunResult:
    agent_name: str
    model: str
    system_prompt: str
    user_prompt: str
    output_text: str
    duration_seconds: float | None = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class PipelineArtifacts:
    intake_report: AgentRunResult
    triage_report: AgentRunResult
    diagnosis_report: AgentRunResult
    treatment_report: AgentRunResult

    def to_dict(self) -> dict:
        return {
            "intake_report": self.intake_report.to_dict(),
            "triage_report": self.triage_report.to_dict(),
            "diagnosis_report": self.diagnosis_report.to_dict(),
            "treatment_report": self.treatment_report.to_dict(),
        }
