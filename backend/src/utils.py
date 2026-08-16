"""Utility functions for the Cisco Network Troubleshooting AI."""

import logging
import sys


def setup_logging(level: int = logging.INFO) -> None:
    """Configure application logging."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("app.log", encoding="utf-8")
        ]
    )
    
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def print_menu() -> None:
    """Print the main menu."""
    print("\n" + "=" * 40)
    print("Cisco Network Troubleshooting AI")
    print("=" * 40)
    print("1. List cases")
    print("2. Diagnose a case")
    print("3. Validate dataset")
    print("4. Evaluate model")
    print("5. Exit")
    print()


def print_cases(cases: list) -> None:
    """Print a formatted list of cases."""
    print(f"\n{'ID':<4} | {'Fault':<35} | {'Concept':<30} | {'Severity'}")
    print("-" * 85)
    for case in cases:
        title = case.title[:34]
        concept = case.concept[:29]
        print(f"{case.case_id:<4} | {title:<35} | {concept:<30} | {case.severity}")


def get_multiline_input(prompt: str) -> str:
    """Get multiline input from user."""
    print(prompt)
    print("(Enter empty line to finish)")
    lines = []
    while True:
        try:
            line = input()
            if line == "":
                break
            lines.append(line)
        except EOFError:
            break
    return "\n".join(lines)