from __future__ import annotations

import importlib.util
import json
from datetime import datetime
from pathlib import Path

from .agents.diagnosis_agent import DiagnosisAgent
from .agents.intake_agent import IntakeAgent
from .agents.treatment_agent import TreatmentAgent
from .agents.triage_agent import TriageAgent
from .llm import LLMClient
from .schemas import PatientCase, PipelineArtifacts
from .settings_loader import load_model_profile, load_prompt_set


def load_settings():
    root_dir = Path(__file__).resolve().parents[2]
    config_path = root_dir / "config" / "config.py"
    mock_config_path = root_dir / "config" / "mock_config.py"
    target_path = config_path if config_path.exists() else mock_config_path

    spec = importlib.util.spec_from_file_location("app_config", target_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load configuration.")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MedicalTriageCoordinator:
    def __init__(
        self,
        *,
        model_profile_name: str | None = None,
        prompt_set_name: str | None = None,
        save_outputs: bool = True,
    ) -> None:
        self.root_dir = Path(__file__).resolve().parents[2]
        self.save_outputs = save_outputs
        self.settings = load_settings()
        api_key = getattr(self.settings, "OPENAI_API_KEY", "")
        if not api_key or "your-openai-api-key" in api_key or "replace-with-your-real" in api_key:
            raise ValueError(
                "Missing a real OpenAI API key. Copy config/mock_config.py to config/config.py and fill it in."
            )

        self.llm_client = LLMClient(
            api_key=api_key,
            base_url=getattr(self.settings, "OPENAI_BASE_URL", None),
        )
        self.model_profile_name = model_profile_name or getattr(self.settings, "ACTIVE_MODEL_PROFILE", "balanced")
        self.prompt_set_name = prompt_set_name or getattr(self.settings, "ACTIVE_PROMPT_SET", "default")
        self.model_profile = load_model_profile(self.root_dir, self.model_profile_name)
        self.prompt_set = load_prompt_set(self.root_dir, self.prompt_set_name)

        self.intake_agent = IntakeAgent(
            name="Intake Agent",
            model=self.model_profile["intake"],
            llm_client=self.llm_client,
            system_prompt_text=self.prompt_set["intake_system"],
            user_prompt_template=self.prompt_set["intake_user"],
        )
        self.triage_agent = TriageAgent(
            name="Triage Agent",
            model=self.model_profile["triage"],
            llm_client=self.llm_client,
            system_prompt_text=self.prompt_set["triage_system"],
            user_prompt_template=self.prompt_set["triage_user"],
        )
        self.diagnosis_agent = DiagnosisAgent(
            name="Diagnosis Agent",
            model=self.model_profile["diagnosis"],
            llm_client=self.llm_client,
            system_prompt_text=self.prompt_set["diagnosis_system"],
            user_prompt_template=self.prompt_set["diagnosis_user"],
        )
        self.treatment_agent = TreatmentAgent(
            name="Treatment Agent",
            model=self.model_profile["treatment"],
            llm_client=self.llm_client,
            system_prompt_text=self.prompt_set["treatment_system"],
            user_prompt_template=self.prompt_set["treatment_user"],
        )

        self.output_root = self.root_dir / getattr(self.settings, "OUTPUT_ROOT", "outputs")

    def run(self, patient_case: PatientCase) -> tuple[PipelineArtifacts, Path | None]:
        run_dir = self._make_run_dir() if self.save_outputs else None
        patient_case_block = patient_case.to_prompt_block()

        intake_report = self.intake_agent.run(patient_case=patient_case_block)
        if run_dir is not None:
            self._write_text(run_dir / "01_intake_report.md", intake_report.output_text)

        triage_report = self.triage_agent.run(
            patient_case=patient_case_block,
            intake_report=intake_report.output_text,
        )
        if run_dir is not None:
            self._write_text(run_dir / "02_triage_report.md", triage_report.output_text)

        diagnosis_report = self.diagnosis_agent.run(
            patient_case=patient_case_block,
            intake_report=intake_report.output_text,
            triage_report=triage_report.output_text,
        )
        if run_dir is not None:
            self._write_text(run_dir / "03_diagnosis_report.md", diagnosis_report.output_text)

        treatment_report = self.treatment_agent.run(
            patient_case=patient_case_block,
            intake_report=intake_report.output_text,
            triage_report=triage_report.output_text,
            diagnosis_report=diagnosis_report.output_text,
        )
        if run_dir is not None:
            self._write_text(run_dir / "04_final_report.md", treatment_report.output_text)

        artifacts = PipelineArtifacts(
            intake_report=intake_report,
            triage_report=triage_report,
            diagnosis_report=diagnosis_report,
            treatment_report=treatment_report,
        )
        if run_dir is not None:
            self._write_json(run_dir / "pipeline_summary.json", artifacts.to_dict())
        return artifacts, run_dir

    def _make_run_dir(self) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir = self.output_root / f"run_{timestamp}"
        run_dir.mkdir(parents=True, exist_ok=True)
        return run_dir

    @staticmethod
    def _write_text(path: Path, content: str) -> None:
        path.write_text(content, encoding="utf-8")

    @staticmethod
    def _write_json(path: Path, payload: dict) -> None:
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
