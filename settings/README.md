# Settings Directory

This directory centralizes experiment settings for the medical triage system.

## Structure

- `model_profiles.py`
  Defines named model bundles such as `balanced`, `fast`, or `strong`.
- `prompt_sets/`
  Contains editable prompt files grouped by prompt-set name.

## How To Switch Models

Edit `config/config.py`:

```python
ACTIVE_MODEL_PROFILE = "balanced"
```

Then update the selected profile inside `settings/model_profiles.py`.

## How To Switch Prompt Sets

Edit `config/config.py`:

```python
ACTIVE_PROMPT_SET = "default"
```

To create a new prompt version:

1. Copy `settings/prompt_sets/default/` to a new folder like `settings/prompt_sets/strict_v2/`
2. Edit the prompt text files
3. Change `ACTIVE_PROMPT_SET` in `config/config.py`

## Prompt File Naming

- `intake_system.txt`
- `intake_user.txt`
- `triage_system.txt`
- `triage_user.txt`
- `diagnosis_system.txt`
- `diagnosis_user.txt`
- `treatment_system.txt`
- `treatment_user.txt`
