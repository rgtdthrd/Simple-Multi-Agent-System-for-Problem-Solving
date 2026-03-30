from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass
class AgentRunResult:
    agent_name: str
    model: str
    system_prompt: str
    user_prompt: str
    output_text: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class PipelineArtifacts:
    idea_brief: AgentRunResult
    market_strategy: AgentRunResult
    final_strategy: AgentRunResult

    def to_dict(self) -> dict:
        return {
            "idea_brief": self.idea_brief.to_dict(),
            "market_strategy": self.market_strategy.to_dict(),
            "final_strategy": self.final_strategy.to_dict(),
        }
