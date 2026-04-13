from __future__ import annotations

from abc import ABC, abstractmethod
from time import perf_counter

from ..schemas import AgentRunResult


class BaseAgent(ABC):
    def __init__(self, name: str, model: str, llm_client, system_prompt_text: str) -> None:
        self.name = name
        self.model = model
        self.llm_client = llm_client
        self._system_prompt_text = system_prompt_text

    @property
    def system_prompt(self) -> str:
        return self._system_prompt_text

    @abstractmethod
    def build_user_prompt(self, **kwargs) -> str:
        raise NotImplementedError

    def run(self, **kwargs) -> AgentRunResult:
        user_prompt = self.build_user_prompt(**kwargs)
        started_at = perf_counter()
        output_text = self.llm_client.generate(
            model=self.model,
            system_prompt=self.system_prompt,
            user_prompt=user_prompt,
        )
        duration_seconds = perf_counter() - started_at
        return AgentRunResult(
            agent_name=self.name,
            model=self.model,
            system_prompt=self.system_prompt,
            user_prompt=user_prompt,
            output_text=output_text,
            duration_seconds=duration_seconds,
        )
