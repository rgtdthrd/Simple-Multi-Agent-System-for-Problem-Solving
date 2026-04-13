# Evaluation Data Format

The normalized evaluation dataset is stored as JSONL.

Each line is one case with:

- `case_id`
- `source_dataset`
- `question`
- `options`
- `gold_answer_idx`
- `gold_answer_text`
- `patient_case`
- `metadata`

## Example

```json
{
  "case_id": "medqa_000001",
  "source_dataset": "MedQA",
  "question": "A 24-year-old woman presents with fever, cough, and pleuritic chest pain...",
  "options": {
    "A": "Pulmonary embolism",
    "B": "Community-acquired pneumonia",
    "C": "Pneumothorax",
    "D": "Asthma exacerbation"
  },
  "gold_answer_idx": "B",
  "gold_answer_text": "Community-acquired pneumonia",
  "patient_case": {
    "age": "24",
    "sex": "female",
    "vitals": "not provided",
    "symptoms": "A 24-year-old woman presents with fever, cough, and pleuritic chest pain.\n\nAnswer options:\nA. Pulmonary embolism\nB. Community-acquired pneumonia\nC. Pneumothorax\nD. Asthma exacerbation",
    "medical_history": "not provided",
    "current_medications": "not provided",
    "allergies": "not provided",
    "duration": "not provided"
  },
  "metadata": {
    "adapter_version": "1.0",
    "notes": "Question stem and options were normalized from MedQA JSONL."
  }
}
```

## Notes

- MedQA is used here mainly for `Diagnosis Agent` and overall report evaluation.
- Because MedQA is not a triage-labeled dataset, triage is evaluated mainly by structure and optional judge scores in this first version.
