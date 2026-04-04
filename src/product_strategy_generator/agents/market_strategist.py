from __future__ import annotations

from .base_agent import BaseAgent


class MarketStrategistAgent(BaseAgent):
    @property
    def system_prompt(self) -> str:
        return (
            """
            Read the high level idea and give a detailed overview of plan and how much effort will it take, give output in such a way that it is prompt for another agent which is going to generate final product strategy. Make sure size of final generated text is friendly for OpenAI's API it should be not too big.
            """

        )

    def build_user_prompt(self, *, idea: str, idea_brief: str) -> str:
        #return f"""
        #        """.strip()
        print(f"-------user prompt for market agent {idea_brief}")

        return idea_brief
        
