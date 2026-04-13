from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_python_module(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load Python module from {path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_model_profile(root_dir: Path, profile_name: str) -> dict[str, str]:
    profile_path = root_dir / "settings" / "model_profiles.py"
    module = _load_python_module("model_profiles", profile_path)
    profiles = getattr(module, "MODEL_PROFILES", {})
    if profile_name not in profiles:
        available = ", ".join(sorted(profiles))
        raise ValueError(f"Unknown model profile '{profile_name}'. Available profiles: {available}")
    return profiles[profile_name]


def load_prompt_set(root_dir: Path, prompt_set_name: str) -> dict[str, str]:
    prompt_dir = root_dir / "settings" / "prompt_sets" / prompt_set_name
    if not prompt_dir.exists():
        raise ValueError(f"Prompt set '{prompt_set_name}' not found at {prompt_dir}")

    prompt_files = {
        "intake_system": prompt_dir / "intake_system.txt",
        "intake_user": prompt_dir / "intake_user.txt",
        "triage_system": prompt_dir / "triage_system.txt",
        "triage_user": prompt_dir / "triage_user.txt",
        "diagnosis_system": prompt_dir / "diagnosis_system.txt",
        "diagnosis_user": prompt_dir / "diagnosis_user.txt",
        "treatment_system": prompt_dir / "treatment_system.txt",
        "treatment_user": prompt_dir / "treatment_user.txt",
    }

    return {key: path.read_text(encoding="utf-8").strip() for key, path in prompt_files.items()}


def render_prompt(template: str, **values: str) -> str:
    rendered = template
    for key, value in values.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)
    return rendered.strip()
