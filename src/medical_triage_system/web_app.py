from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from .coordinator import MedicalTriageCoordinator, load_settings
from .schemas import PatientCase
from .settings_loader import list_model_profiles, list_prompt_sets


class AnalyzeRequest(BaseModel):
    age: str = Field(default="not provided")
    sex: str = Field(default="not provided")
    vitals: str = Field(min_length=1)
    symptoms: str = Field(min_length=1)
    medical_history: str = Field(default="not provided")
    current_medications: str = Field(default="not provided")
    allergies: str = Field(default="not provided")
    duration: str = Field(default="not provided")
    model_profile: str | None = Field(default=None)
    prompt_set: str | None = Field(default=None)


def _build_patient_case(payload: AnalyzeRequest) -> PatientCase:
    return PatientCase(
        age=payload.age.strip() or "not provided",
        sex=payload.sex.strip() or "not provided",
        vitals=payload.vitals.strip(),
        symptoms=payload.symptoms.strip(),
        medical_history=payload.medical_history.strip() or "not provided",
        current_medications=payload.current_medications.strip() or "not provided",
        allergies=payload.allergies.strip() or "not provided",
        duration=payload.duration.strip() or "not provided",
    )


ROOT_DIR = Path(__file__).resolve().parents[2]
WEB_DIR = ROOT_DIR / "src" / "medical_triage_system" / "web"

app = FastAPI(
    title="Medical Triage Multi-Agent System",
    description="A web interface for the multi-agent medical triage pipeline.",
    version="1.0.0",
)
templates = Jinja2Templates(directory=str(WEB_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(WEB_DIR / "static")), name="static")


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    settings = load_settings()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "active_model_profile": getattr(settings, "ACTIVE_MODEL_PROFILE", "model_1"),
            "active_prompt_set": getattr(settings, "ACTIVE_PROMPT_SET", "default"),
            "model_profiles": list_model_profiles(ROOT_DIR),
            "prompt_sets": list_prompt_sets(ROOT_DIR),
        },
    )


@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> FileResponse:
    return FileResponse(WEB_DIR / "static" / "favicon.svg", media_type="image/svg+xml")


@app.get("/api/options")
def get_options() -> dict:
    settings = load_settings()
    return {
        "model_profiles": list_model_profiles(ROOT_DIR),
        "prompt_sets": list_prompt_sets(ROOT_DIR),
        "active_model_profile": getattr(settings, "ACTIVE_MODEL_PROFILE", "model_1"),
        "active_prompt_set": getattr(settings, "ACTIVE_PROMPT_SET", "default"),
    }


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/analyze")
def analyze(payload: AnalyzeRequest) -> dict:
    try:
        coordinator = MedicalTriageCoordinator(
            model_profile_name=payload.model_profile,
            prompt_set_name=payload.prompt_set,
        )
        patient_case = _build_patient_case(payload)
        artifacts, run_dir = coordinator.run(patient_case)
    except Exception as exc:  # pragma: no cover - surfaced to UI for debugging
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {
        "run_dir": str(run_dir) if run_dir else None,
        "model_profile": coordinator.model_profile_name,
        "prompt_set": coordinator.prompt_set_name,
        "reports": {
            "intake": artifacts.intake_report.output_text,
            "triage": artifacts.triage_report.output_text,
            "diagnosis": artifacts.diagnosis_report.output_text,
            "treatment": artifacts.treatment_report.output_text,
        },
        "durations": {
            "intake": artifacts.intake_report.duration_seconds,
            "triage": artifacts.triage_report.duration_seconds,
            "diagnosis": artifacts.diagnosis_report.duration_seconds,
            "treatment": artifacts.treatment_report.duration_seconds,
        },
    }
