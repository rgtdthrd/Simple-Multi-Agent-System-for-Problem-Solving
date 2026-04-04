from __future__ import annotations

import argparse

from .coordinator import ProductStrategyCoordinator


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a product strategy from a raw idea.")
    parser.add_argument(
        "--idea",
        required=True,
        help="A raw product idea that the multi-agent system will turn into a product strategy.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    
    coordinator = ProductStrategyCoordinator()
    artifacts, run_dir = coordinator.run(args.idea)

    print("Product strategy generated successfully.")
    print(f"Idea is: {args.idea}")
    print(f"Run directory: {run_dir}")
    print()
    print("Final strategy:")
    print(artifacts.final_strategy.output_text)


if __name__ == "__main__":
    main()
