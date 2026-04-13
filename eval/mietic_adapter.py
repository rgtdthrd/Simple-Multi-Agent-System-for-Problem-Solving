from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Normalize raw MIETIC.csv into evaluation JSONL format.")
    parser.add_argument("--input", required=True, help="Path to raw MIETIC.csv")
    parser.add_argument("--output", required=True, help="Path to output JSONL")
    parser.add_argument("--limit", type=int, default=100, help="Maximum number of rows to export")
    return parser.parse_args()


def parse_esi_from_output(text: str) -> int | None:
    match = re.search(r"\besi(?:\s*level)?\s*[-:]?\s*([1-5])\b", text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


def map_esi_to_urgency(esi: int | None) -> str:
    mapping = {
        1: "emergency now",
        2: "urgent same-day evaluation",
        3: "urgent same-day evaluation",
        4: "routine medical follow-up",
        5: "self-care with monitoring",
    }
    return mapping.get(esi, "urgent same-day evaluation")


def extract_field(pattern: str, text: str, default: str = "not provided") -> str:
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).strip(" .;,")
    return default


def build_patient_case(input_text: str) -> dict:
    age = extract_field(r"(\d{1,3})-year-old", input_text)
    sex = extract_field(r"\b(male|female|man|woman)\b", input_text)
    temp = extract_field(r"(temp(?:erature)?[^,.;]*)", input_text)
    hr = extract_field(r"(hr[^,.;]*|heart rate[^,.;]*)", input_text)
    bp = extract_field(r"(bp[^,.;]*|blood pressure[^,.;]*)", input_text)
    spo2 = extract_field(r"(spo2[^,.;]*|oxygen saturation[^,.;]*)", input_text)
    duration = extract_field(r"for ([^.,;]+)", input_text)
    medical_history = extract_field(r"(history of [^.;]*)", input_text)

    vitals_parts = [part for part in [temp, hr, bp, spo2] if part != "not provided"]
    vitals = ", ".join(vitals_parts) if vitals_parts else "not provided"

    return {
        "age": age,
        "sex": sex,
        "vitals": vitals,
        "symptoms": input_text,
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

    with input_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    written = 0
    with output_path.open("w", encoding="utf-8") as out_f:
        for idx, row in enumerate(rows, start=1):
            if written >= args.limit:
                break

            instruction = row.get("instruction", "").strip()
            input_text = row.get("input", "").strip()
            gold_output = row.get("output", "").strip()
            if not input_text or not gold_output:
                continue

            gold_esi = parse_esi_from_output(gold_output)
            normalized = {
                "case_id": f"mietic_{idx:06d}",
                "source_dataset": "MIETIC",
                "instruction": instruction,
                "input_text": input_text,
                "gold_output_text": gold_output,
                "gold_esi": gold_esi,
                "gold_urgency_bucket": map_esi_to_urgency(gold_esi),
                "patient_case": build_patient_case(input_text),
                "metadata": {
                    "adapter_version": "1.0",
                    "notes": "Patient-case fields were heuristically derived from MIETIC input text."
                }
            }
            out_f.write(json.dumps(normalized, ensure_ascii=False) + "\n")
            written += 1

    print(f"Wrote {written} normalized cases to {output_path}")


if __name__ == "__main__":
    main()
