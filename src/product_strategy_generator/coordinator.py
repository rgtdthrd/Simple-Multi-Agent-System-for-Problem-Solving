from __future__ import annotations

import importlib.util
import json
from datetime import datetime
from pathlib import Path

from .agents.idea_analyst import IdeaAnalystAgent
from .agents.market_strategist import MarketStrategistAgent
from .agents.strategy_writer import StrategyWriterAgent
from .llm import LLMClient
from .schemas import PipelineArtifacts


def load_settings():
    root_dir = Path(__file__).resolve().parents[2]
    config_path = root_dir / "config" / "config.py"
    mock_config_path = root_dir / "config" / "mock_config.py"
    target_path = config_path if config_path.exists() else mock_config_path

    spec = importlib.util.spec_from_file_location("app_config", target_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load configuration.")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ProductStrategyCoordinator:
    def __init__(self) -> None:
        self.root_dir = Path(__file__).resolve().parents[2]
        self.settings = load_settings()
        api_key = getattr(self.settings, "OPENAI_API_KEY", "")
        if not api_key or "your-openai-api-key" in api_key or "replace-with-your-real" in api_key:
            raise ValueError(
                "Missing a real OpenAI API key. Copy config/mock_config.py to config/config.py and fill it in."
            )

        self.llm_client = LLMClient(
            api_key=api_key,
            base_url=getattr(self.settings, "OPENAI_BASE_URL", None),
        )

        self.idea_analyst = IdeaAnalystAgent(
            name="Idea Analyst",
            model=self.settings.IDEA_ANALYST_MODEL,
            llm_client=self.llm_client,
        )
        self.market_strategist = MarketStrategistAgent(
            name="Market Strategist",
            model=self.settings.MARKET_STRATEGIST_MODEL,
            llm_client=self.llm_client,
        )
        self.strategy_writer = StrategyWriterAgent(
            name="Strategy Writer",
            model=self.settings.STRATEGY_WRITER_MODEL,
            llm_client=self.llm_client,
        )

        self.output_root = self.root_dir / getattr(self.settings, "OUTPUT_ROOT", "outputs")

    def run(self, idea: str) -> tuple[PipelineArtifacts, Path]:
        run_dir = self._make_run_dir()

        idea_brief = self.idea_analyst.run(idea=idea)
        self._write_text(run_dir / "01_idea_brief.md", idea_brief.output_text)

        market_strategy = self.market_strategist.run(
            idea=idea,
            idea_brief=idea_brief.output_text,
        )
        self._write_text(run_dir / "02_market_strategy.md", market_strategy.output_text)

        final_strategy = self.strategy_writer.run(
            idea=idea,
            idea_brief=idea_brief.output_text,
            market_strategy=market_strategy.output_text,
        )
        self._write_text(run_dir / "03_final_product_strategy.md", final_strategy.output_text)

        artifacts = PipelineArtifacts(
            idea_brief=idea_brief,
            market_strategy=market_strategy,
            final_strategy=final_strategy,
        )
        self._write_json(run_dir / "pipeline_summary.json", artifacts.to_dict())
        return artifacts, run_dir

    def _make_run_dir(self) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir = self.output_root / f"run_{timestamp}"
        run_dir.mkdir(parents=True, exist_ok=True)
        return run_dir

    @staticmethod
    def _write_text(path: Path, content: str) -> None:
        path.write_text(content, encoding="utf-8")

    @staticmethod
    def _write_json(path: Path, payload: dict) -> None:
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
