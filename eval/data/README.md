# Evaluation Data Format

The normalized evaluation dataset is stored as JSONL.

Each line is one case with:

- `case_id`
- `source_dataset`
- `instruction`
- `input_text`
- `gold_output_text`
- `gold_esi`
- `gold_urgency_bucket`
- `patient_case`
- `metadata`

## Example

```json
{
  "case_id": "mietic_000001",
  "source_dataset": "MIETIC",
  "instruction": "Assign the appropriate emergency triage level.",
  "input_text": "A 67-year-old male presents with fever, productive cough, and shortness of breath for two days...",
  "gold_output_text": "ESI Level 2. High-risk respiratory complaint...",
  "gold_esi": 2,
  "gold_urgency_bucket": "urgent same-day evaluation",
  "patient_case": {
    "age": "67",
    "sex": "male",
    "vitals": "Temp 38.1C, HR 112, BP 96/60, SpO2 92%",
    "symptoms": "Fever, productive cough, shortness of breath",
    "medical_history": "COPD, hypertension",
    "current_medications": "not provided",
    "allergies": "not provided",
    "duration": "2 days"
  },
  "metadata": {
    "adapter_version": "1.0",
    "notes": "Fields may be partially heuristic when derived from MIETIC input text."
  }
}
```

## ESI To Urgency Mapping

- `ESI-1 -> emergency now`
- `ESI-2 -> urgent same-day evaluation`
- `ESI-3 -> urgent same-day evaluation`
- `ESI-4 -> routine medical follow-up`
- `ESI-5 -> self-care with monitoring`
