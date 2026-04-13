from __future__ import annotations

from .base_agent import BaseAgent
from ..settings_loader import render_prompt


class TriageAgent(BaseAgent):
    def __init__(self, name: str, model: str, llm_client, system_prompt_text: str, user_prompt_template: str) -> None:
        super().__init__(name=name, model=model, llm_client=llm_client, system_prompt_text=system_prompt_text)
        self.user_prompt_template = user_prompt_template

    def build_user_prompt(self, *, patient_case: str, intake_report: str) -> str:
        return render_prompt(
            self.user_prompt_template,
            patient_case=patient_case,
            intake_report=intake_report,
        )
