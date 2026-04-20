from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from time import perf_counter

from src.medical_triage_system.coordinator import MedicalTriageCoordinator
from src.medical_triage_system.schemas import PatientCase

from .medqa_adapter import build_patient_case, normalize_options, resolve_gold_answer
from .metrics import score_case_result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run evaluation benchmark across model/profile combinations.")
    parser.add_argument("--dataset", required=True, help="Path to normalized evaluation JSONL dataset.")
    parser.add_argument("--matrix", required=True, help="Path to benchmark matrix JSON.")
    parser.add_argument("--output-dir", default="eval/outputs", help="Directory for benchmark results.")
    return parser.parse_args()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def save_json(path: Path, payload: dict | list) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def save_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + ("\n" if rows else ""),
        encoding="utf-8",
    )


def normalize_case(case: dict, case_index: int) -> dict:
    if "patient_case" in case:
        normalized = dict(case)
        normalized.setdefault("case_id", f"case_{case_index:06d}")
        normalized.setdefault("source_dataset", "MedQA")
        normalized.setdefault("question", case.get("question") or case.get("input_text"))
        normalized.setdefault("options", case.get("options", {}))
        normalized.setdefault("gold_answer_idx", case.get("gold_answer_idx"))
        normalized.setdefault("gold_answer_text", case.get("gold_answer_text") or case.get("gold_output_text"))
        return normalized

    question = str(case.get("question") or case.get("query") or case.get("input") or "").strip()
    options = normalize_options(case.get("options"))
    gold_answer_idx, gold_answer_text = resolve_gold_answer(case, options)

    return {
        "case_id": case.get("case_id", f"medqa_{case_index:06d}"),
        "source_dataset": case.get("source_dataset", "MedQA"),
        "question": question,
        "options": options,
        "gold_answer_idx": gold_answer_idx,
        "gold_answer_text": gold_answer_text,
        "patient_case": build_patient_case(question, options),
        "metadata": case.get("metadata", {}),
    }


def main() -> None:
    args = parse_args()
    dataset_path = Path(args.dataset)
    matrix_path = Path(args.matrix)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    dataset = load_jsonl(dataset_path)
    matrix = load_json(matrix_path)
    max_cases = matrix.get("max_cases")
    raw_cases = dataset[:max_cases] if max_cases else dataset
    cases = [normalize_case(case, idx) for idx, case in enumerate(raw_cases, start=1)]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = output_dir / f"benchmark_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    save_json(
        run_dir / "run_manifest.json",
        {
            "dataset": str(dataset_path),
            "matrix": matrix,
            "num_cases": len(cases),
            "started_at": timestamp,
        },
    )

    all_rows: list[dict] = []
    for model_profile in matrix["model_profiles"]:
        for prompt_set in matrix["prompt_sets"]:
            coordinator = MedicalTriageCoordinator(
                model_profile_name=model_profile,
                prompt_set_name=prompt_set,
                save_outputs=False,
            )
            for case in cases:
                patient_case = PatientCase(**case["patient_case"])
                started_at = perf_counter()
                artifacts, _ = coordinator.run(patient_case)
                total_duration = perf_counter() - started_at

                row = {
                    "case_id": case["case_id"],
                    "source_dataset": case["source_dataset"],
                    "model_profile": model_profile,
                    "prompt_set": prompt_set,
                    "question": case.get("question"),
                    "options": case.get("options", {}),
                    "gold_answer_idx": case.get("gold_answer_idx"),
                    "gold_answer_text": case.get("gold_answer_text"),
                    "input_text": case.get("question") or case.get("input_text"),
                    "gold_output_text": case.get("gold_answer_text") or case.get("gold_output_text"),
                    "patient_case": case["patient_case"],
                    "intake_output": artifacts.intake_report.output_text,
                    "triage_output": artifacts.triage_report.output_text,
                    "diagnosis_output": artifacts.diagnosis_report.output_text,
                    "treatment_output": artifacts.treatment_report.output_text,
                    "intake_duration_seconds": artifacts.intake_report.duration_seconds,
                    "triage_duration_seconds": artifacts.triage_report.duration_seconds,
                    "diagnosis_duration_seconds": artifacts.diagnosis_report.duration_seconds,
                    "treatment_duration_seconds": artifacts.treatment_report.duration_seconds,
                    "total_duration_seconds": total_duration,
                }
                row.update(score_case_result(row))
                all_rows.append(row)

    save_jsonl(run_dir / "case_results.jsonl", all_rows)
    print(f"Saved benchmark case results to {run_dir / 'case_results.jsonl'}")


if __name__ == "__main__":
    main()
