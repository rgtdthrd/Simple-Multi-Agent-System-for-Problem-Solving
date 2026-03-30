from __future__ import annotations

from abc import ABC, abstractmethod

from ..schemas import AgentRunResult


class BaseAgent(ABC):
    def __init__(self, name: str, model: str, llm_client) -> None:
        self.name = name
        self.model = model
        self.llm_client = llm_client

    @abstractmethod
    def build_user_prompt(self, **kwargs) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        raise NotImplementedError

    def run(self, **kwargs) -> AgentRunResult:
        user_prompt = self.build_user_prompt(**kwargs)
        output_text = self.llm_client.generate(
            model=self.model,
            system_prompt=self.system_prompt,
            user_prompt=user_prompt,
        )
        return AgentRunResult(
            agent_name=self.name,
            model=self.model,
            system_prompt=self.system_prompt,
            user_prompt=user_prompt,
            output_text=output_text,
        )
