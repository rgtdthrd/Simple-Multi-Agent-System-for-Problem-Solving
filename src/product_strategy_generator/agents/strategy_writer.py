from __future__ import annotations

from .base_agent import BaseAgent


class StrategyWriterAgent(BaseAgent):
    @property
    def system_prompt(self) -> str:
        return (
            """
            Read the report provided by user and generate a step by step process to implement this idea also cover anything realted to strategy and give detailled response to user.
            """
        )

    def build_user_prompt(
        self,
        *,
        idea: str,
        idea_brief: str,
        market_strategy: str,
    ) -> str:
        #return f"""
        #        """.strip()
        print(f"-------user prompt for final agent {market_strategy}")
        return market_strategy
