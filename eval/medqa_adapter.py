from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Normalize raw MedQA JSONL into evaluation JSONL format.")
    parser.add_argument("--input", required=True, help="Path to raw MedQA JSONL")
    parser.add_argument("--output", required=True, help="Path to output JSONL")
    parser.add_argument("--limit", type=int, default=100, help="Maximum number of rows to export")
    return parser.parse_args()


def extract_field(pattern: str, text: str, default: str = "not provided") -> str:
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).strip(" .;,")
    return default


def normalize_options(raw_options) -> dict[str, str]:
    if isinstance(raw_options, dict):
        return {str(key).strip(): str(value).strip() for key, value in raw_options.items()}
    if isinstance(raw_options, list):
        option_keys = ["A", "B", "C", "D", "E", "F"]
        return {option_keys[idx]: str(value).strip() for idx, value in enumerate(raw_options) if idx < len(option_keys)}
    return {}


def resolve_gold_answer(row: dict, options: dict[str, str]) -> tuple[str | None, str | None]:
    answer_idx = row.get("answer_idx") or row.get("answer") or row.get("label")
    answer_text = row.get("answer_text")

    if answer_idx is not None:
        answer_idx = str(answer_idx).strip()
        if answer_idx in options:
            return answer_idx, options[answer_idx]
        upper = answer_idx.upper()
        if upper in options:
            return upper, options[upper]
        if answer_idx.isdigit():
            idx = int(answer_idx)
            ordered = list(options.keys())
            if 0 <= idx < len(ordered):
                resolved_idx = ordered[idx]
                return resolved_idx, options[resolved_idx]

    if answer_text:
        answer_text = str(answer_text).strip()
        for option_key, option_value in options.items():
            if option_value.strip().lower() == answer_text.lower():
                return option_key, option_value
        return None, answer_text

    return None, None


def build_patient_case(question: str, options: dict[str, str]) -> dict:
    age = extract_field(r"(\d{1,3})-year-old", question)
    sex = extract_field(r"\b(male|female|man|woman)\b", question)
    temp = extract_field(r"(temp(?:erature)?[^,.;]*)", question)
    hr = extract_field(r"(hr[^,.;]*|heart rate[^,.;]*)", question)
    bp = extract_field(r"(bp[^,.;]*|blood pressure[^,.;]*)", question)
    spo2 = extract_field(r"(spo2[^,.;]*|oxygen saturation[^,.;]*)", question)
    duration = extract_field(r"for ([^.,;]+)", question)
    medical_history = extract_field(r"(history of [^.;]*)", question)

    vitals_parts = [part for part in [temp, hr, bp, spo2] if part != "not provided"]
    vitals = ", ".join(vitals_parts) if vitals_parts else "not provided"
    options_block = "\n".join(f"{key}. {value}" for key, value in options.items())
    symptoms = f"{question}\n\nAnswer options:\n{options_block}" if options_block else question

    return {
        "age": age,
        "sex": sex,
        "vitals": vitals,
        "symptoms": symptoms,
        "medical_history": medical_history,
        "current_medications": "not provided",
        "allergies": "not provided",
        "duration": duration,
    }


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows = [json.loads(line) for line in input_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    written = 0
    with output_path.open("w", encoding="utf-8") as out_f:
        for idx, row in enumerate(rows, start=1):
            if written >= args.limit:
                break

            question = str(row.get("question") or row.get("query") or row.get("input") or "").strip()
            options = normalize_options(row.get("options"))
            if not question or not options:
                continue

            gold_answer_idx, gold_answer_text = resolve_gold_answer(row, options)
            normalized = {
                "case_id": f"medqa_{idx:06d}",
                "source_dataset": "MedQA",
                "question": question,
                "options": options,
                "gold_answer_idx": gold_answer_idx,
                "gold_answer_text": gold_answer_text,
                "patient_case": build_patient_case(question, options),
                "metadata": {
                    "adapter_version": "1.0",
                    "notes": "Question stem and options were normalized from MedQA JSONL."
                }
            }
            out_f.write(json.dumps(normalized, ensure_ascii=False) + "\n")
            written += 1

    print(f"Wrote {written} normalized cases to {output_path}")


if __name__ == "__main__":
    main()
