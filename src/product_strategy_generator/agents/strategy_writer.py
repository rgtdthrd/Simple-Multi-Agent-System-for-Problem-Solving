from __future__ import annotations

from .base_agent import BaseAgent


class StrategyWriterAgent(BaseAgent):
    @property
    def system_prompt(self) -> str:
        return (
            """
            """
        )

    def build_user_prompt(
        self,
        *,
        idea: str,
        idea_brief: str,
        market_strategy: str,
    ) -> str:
        return f"""
                """.strip()
