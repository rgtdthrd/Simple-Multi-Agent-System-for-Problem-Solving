from __future__ import annotations

from .base_agent import BaseAgent


class IdeaAnalystAgent(BaseAgent):
    @property
    def system_prompt(self) -> str:
        return (
            """
            Just tell briefly, from high level how user's idea can be implemnted. Your output should look like a prompt which can be given to another agent which can read it and work towards producing a strategy. It should be small like one paragraph.
            """
        )

    def build_user_prompt(self, *, idea: str) -> str:
        #return f"""
        #        """.strip()
        return idea
