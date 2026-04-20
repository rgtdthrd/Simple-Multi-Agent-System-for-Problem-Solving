"""
Named model bundles for experiments.

Each model profile points to one provider from config/config.py
and one model name used across all four agents by default.
Replace the placeholder model names below with the actual models you want to test.
"""

MODEL_PROFILES = {
    "model_1": {
        "provider": "provider_1",
        "intake": "minimax/minimax-m2.5:free",
        "triage": "minimax/minimax-m2.5:free",
        "diagnosis": "minimax/minimax-m2.5:free",
        "treatment": "minimax/minimax-m2.5:free",
    },
    "model_2": {
        "provider": "provider_2",
        "intake": "nvidia/nemotron-3-super-120b-a12b:free",
        "triage": "nvidia/nemotron-3-super-120b-a12b:free",
        "diagnosis": "nvidia/nemotron-3-super-120b-a12b:free",
        "treatment": "nvidia/nemotron-3-super-120b-a12b:free",
    },
    "model_3": {
        "provider": "provider_3",
        "intake": "openrouter/elephant-alpha",
        "triage": "openrouter/elephant-alpha",
        "diagnosis": "openrouter/elephant-alpha",
        "treatment": "openrouter/elephant-alpha",
    },
    "model_4": {
        "provider": "provider_4",
        "intake": "google/gemma-4-31b-it:free",
        "triage": "google/gemma-4-31b-it:free",
        "diagnosis": "google/gemma-4-31b-it:free",
        "treatment": "google/gemma-4-31b-it:free",
    },
}
