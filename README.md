# Medical Triage Multi-Agent System

A multi-agent system that takes patient input and produces a structured report with intake normalization, urgency classification, possible disease categories, reasoning, and cautious treatment-path guidance.

## Safety Note

This repository is for educational and prototyping purposes only.
It is not a medical device, does not provide a real diagnosis, and should not replace a licensed clinician.
If symptoms could represent an emergency, the patient should seek immediate professional care.

## Overview

The system uses four specialized agents that pass text outputs to one another through a coordinator:

1. `Intake Agent`
   Structures user input into a clean intake summary.
2. `Triage Agent`
   Assigns an urgency level and highlights red flags.
3. `Diagnosis Agent`
   Produces a cautious differential diagnosis.
4. `Treatment Agent`
   Generates the final integrated report with general management pathways and next steps.

## Workflow

```text
User Input
   |
   v
Intake Agent
   |
   v
Triage Agent
   |
   v
Diagnosis Agent
   |
   v
Treatment Agent
   |
   v
Final Output
```

## Project Structure

```text
.
|-- config/
|   |-- config.py            # local only, ignored by git
|   `-- mock_config.py       # safe template for GitHub
|-- settings/
|   |-- model_profiles.py    # named model bundles
|   `-- prompt_sets/         # editable prompt directories
|-- outputs/                 # generated reports, ignored by git
|-- src/
|   |-- __init__.py
|   `-- medical_triage_system/
|       |-- agents/
|       |   |-- base_agent.py
|       |   |-- intake_agent.py
|       |   |-- triage_agent.py
|       |   |-- diagnosis_agent.py
|       |   `-- treatment_agent.py
|       |-- coordinator.py
|       |-- llm.py
|       |-- main.py
|       `-- schemas.py
|-- LICENSE
|-- README.md
`-- requirements.txt
```

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Copy the example config:

```bash
copy config\mock_config.py config\config.py
```

3. Edit `config/config.py` and add your API key.
4. Choose the active model profile and prompt set in `config/config.py`.

## Experiment Config

Model and prompt tuning now live in `settings/`:

- `settings/model_profiles.py` defines reusable model combinations
- `settings/prompt_sets/default/` stores the current agent prompts
- `config/config.py` selects which model profile and prompt set are active

To test a new prompt version, copy `settings/prompt_sets/default/` into a new folder and switch `ACTIVE_PROMPT_SET`.

## Run

```bash
python -m src.medical_triage_system.main --age "21" --sex "female" --vitals "Temp 38.3C, HR 108, BP 110/70, SpO2 98%" --symptoms "Fever, sore throat, fatigue, swollen neck glands" --history "No chronic illness" --medications "Ibuprofen as needed" --allergies "Penicillin" --duration "3 days"
```

## Output

Each run creates a folder inside `outputs/` containing:

- `01_intake_report.md`
- `02_triage_report.md`
- `03_diagnosis_report.md`
- `04_final_report.md`
- `pipeline_summary.json`

## Why This Design Works

- Each agent has a single responsibility.
- The pipeline is easy to inspect and debug because every handoff is saved.
- Triage is separated from diagnosis, which is safer and easier to reason about.
- The final report integrates all previous stages into a single patient-facing summary.
