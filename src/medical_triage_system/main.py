from __future__ import annotations

import argparse

from .coordinator import MedicalTriageCoordinator
from .schemas import PatientCase


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a multi-agent medical triage report from patient input."
    )
    parser.add_argument("--age", default="not provided", help="Patient age or age range.")
    parser.add_argument("--sex", default="not provided", help="Patient sex.")
    parser.add_argument("--vitals", required=True, help="Reported vitals such as temperature, heart rate, BP, SpO2.")
    parser.add_argument("--symptoms", required=True, help="Primary symptoms and relevant context.")
    parser.add_argument("--history", default="not provided", help="Relevant past medical history.")
    parser.add_argument("--medications", default="not provided", help="Current medications.")
    parser.add_argument("--allergies", default="not provided", help="Known allergies.")
    parser.add_argument("--duration", default="not provided", help="How long the symptoms have been present.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    patient_case = PatientCase(
        age=args.age,
        sex=args.sex,
        vitals=args.vitals,
        symptoms=args.symptoms,
        medical_history=args.history,
        current_medications=args.medications,
        allergies=args.allergies,
        duration=args.duration,
    )

    coordinator = MedicalTriageCoordinator()
    artifacts, run_dir = coordinator.run(patient_case)

    print("Medical triage report generated successfully.")
    print(f"Run directory: {run_dir}")
    print()
    print("Final report:")
    print(artifacts.treatment_report.output_text)


if __name__ == "__main__":
    main()
