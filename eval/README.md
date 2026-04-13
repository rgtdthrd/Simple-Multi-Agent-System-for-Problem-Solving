# Evaluation Framework

This directory contains the evaluation framework for the medical triage multi-agent system.

## Goal

Evaluate the system on MedQA using:

- per-agent metrics
- end-to-end metrics
- experiment sweeps across model profiles and prompt sets
- result aggregation to identify the best configuration

## Layout

```text
eval/
|-- configs/
|   |-- benchmark_matrix.json
|   `-- scoring_weights.json
|-- data/
|   |-- README.md
|   `-- normalized_medqa_template.jsonl
|-- outputs/
|   `-- .gitkeep
|-- aggregate_results.py
|-- judge.py
|-- metrics.py
|-- medqa_adapter.py
|-- parsers.py
|-- runner.py
`-- schemas.py
```

## Recommended Workflow

1. Download a MedQA JSONL split.
2. Convert it into normalized JSONL:

```bash
python -m eval.medqa_adapter --input path\to\US_qbank.jsonl --output eval\data\medqa_eval.jsonl --limit 200
```

3. Edit `eval/configs/benchmark_matrix.json` to choose model profiles and prompt sets.
4. Run the benchmark:

```bash
python -m eval.runner --dataset eval\data\medqa_eval.jsonl --matrix eval\configs\benchmark_matrix.json
```

5. Aggregate the results and rank combinations:

```bash
python -m eval.aggregate_results --input eval\outputs\benchmark_YYYYMMDD_HHMMSS\case_results.jsonl --weights eval\configs\scoring_weights.json
```

6. Optionally run LLM-as-a-judge on the case outputs:

```bash
python -m eval.judge --input eval\outputs\benchmark_YYYYMMDD_HHMMSS\case_results.jsonl --output eval\outputs\benchmark_YYYYMMDD_HHMMSS\judged_case_results.jsonl
```

## Metrics

### Intake Agent

- `intake_section_coverage`
- optional judge grounding score

### Triage Agent

- `triage_section_coverage`
- optional judge safety score

### Diagnosis Agent

- `diagnosis_top1_accuracy`
- `diagnosis_top3_accuracy`
- `diagnosis_contains_gold_answer`
- `diagnosis_section_coverage`
- optional judge plausibility score
- optional judge grounding score

### Treatment Agent

- `treatment_section_coverage`
- `final_report_section_coverage`
- optional judge safety score
- optional judge actionability score

### End-to-End

- `average_agent_latency`
- composite weighted score from `scoring_weights.json`

## Important Limitation

MedQA is primarily a diagnosis-style multiple-choice dataset, so the strongest automatic gold-label evaluation is for the diagnosis stage.
Triage and treatment are evaluated mainly with structure checks plus optional LLM-as-a-judge scoring in this first version.
