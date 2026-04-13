from __future__ import annotations

from openai import OpenAI


class LLMClient:
    def __init__(self, api_key: str, base_url: str | None = None) -> None:
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def generate(self, model: str, system_prompt: str, user_prompt: str) -> str:
        response = self.client.responses.create(
            model=model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.output_text.strip()
