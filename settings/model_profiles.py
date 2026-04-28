"""
Named model bundles for experiments.

Each model profile points to one provider from config/config.py
and one model name used across all four agents by default.
Replace the placeholder model names below with the actual models you want to test.
"""

MODEL_PROFILES = {
    "model_1": {
        "provider": "provider_1",
        "intake": "google/gemma-4-31b-it",
        "triage": "google/gemma-4-31b-it",
        "diagnosis": "google/gemma-4-31b-it",
        "treatment": "google/gemma-4-31b-it",
    },
    "model_2": {
        "provider": "provider_2",
        "intake": "qwen/qwen3.6-plus",
        "triage": "qwen/qwen3.6-plus",
        "diagnosis": "qwen/qwen3.6-plus",
        "treatment": "qwen/qwen3.6-plus",
    },
    "model_3": {
        "provider": "provider_3",
        "intake": "openai/gpt-5.4-mini",
        "triage": "openai/gpt-5.4-mini",
        "diagnosis": "openai/gpt-5.4-mini",
        "treatment": "openai/gpt-5.4-mini",
    },
    "model_4": {
        "provider": "provider_4",
        "intake": "minimax/minimax-m2.7",
        "triage": "minimax/minimax-m2.7",
        "diagnosis": "minimax/minimax-m2.7",
        "treatment": "minimax/minimax-m2.7",
    },
}
