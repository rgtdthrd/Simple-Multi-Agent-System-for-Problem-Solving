from __future__ import annotations

from .base_agent import BaseAgent


class MarketStrategistAgent(BaseAgent):
    @property
    def system_prompt(self) -> str:
        return (
            """
            """

        )

    def build_user_prompt(self, *, idea: str, idea_brief: str) -> str:
        return f"""
                """.strip()
