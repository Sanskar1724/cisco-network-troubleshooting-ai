"""Main CLI entry point for the Cisco Network Troubleshooting AI."""

import sys
from src.config import OPENROUTER_API_KEY
from src.data_loader import load_cases, validate_dataset, print_validation_report, get_case
from src.evidence_parser import load_evidence, parse_evidence_file
from src.diagnosis import diagnose, format_diagnosis
from src.evaluator import evaluate_all_cases, print_evaluation_report
from src.utils import setup_logging, print_menu, print_cases, get_multiline_input
from src.models import Evidence
from src.human_review import HumanReview, interactive_review, ReviewStatus
from src.dashboard import generate_dashboard, Dashboard
from src.rule_checker import run_rule_checker

import logging
logger = logging.getLogger(__name__)


def check_config() -> bool:
    """Check if required configuration is present."""
    if not OPENROUTER_API_KEY:
        print("ERROR: OPENROUTER_API_KEY not set.")
        print("Please copy .env.example to .env and add your API key.")
        return False
    return True


def cmd_list_cases() -> None:
    """List all cases."""
    cases = load_cases()
    print_cases(cases)


def cmd_diagnose() -> None:
    """Diagnose a case with user-provided evidence."""
    if not check_config():
        return
    
    try:
        case_id_str = input("Enter case ID (or press Enter for auto-detect): ").strip()
        case_id = int(case_id_str) if case_id_str else None
    except ValueError:
        print("Invalid case ID")
        return
    
    print("\nEnter network evidence (multiline, empty line to finish):")
    evidence_text = get_multiline_input("Evidence:")
    
    if case_id:
        evidence = Evidence(case_id=case_id)
    else:
        evidence = Evidence()
    
    if evidence_text:
        evidence.other_cli_output = evidence_text
    
    try:
        # Run rule checker first
        print("\nRunning deterministic rule checks...")
        rule_results = run_rule_checker(evidence, get_case(case_id) if case_id else None)
        if rule_results:
            print(f"Rule checker found {len(rule_results)} issue(s):")
            for r in rule_results:
                print(f"  [{r['severity']}] {r['check']}: {r['message']}")
        else:
            print("No deterministic issues found.")
        
        # Run AI diagnosis
        print("\nRunning AI diagnosis...")
        result = diagnose(evidence, case_id)
        print("\n" + format_diagnosis(result))
        
        # Offer human review
        if case_id:
            case = get_case(case_id)
            if case:
                review = HumanReview()
                review_choice = input("\nLog human review? (y/n): ").strip().lower()
                if review_choice == 'y':
                    interactive_review(case_id, case.title, result)
                    
    except Exception as e:
        logger.error(f"Diagnosis failed: {e}")
        print(f"Error: {e}")


def cmd_validate() -> None:
    """Validate the dataset."""
    report = validate_dataset()
    print_validation_report(report)


def cmd_evaluate() -> None:
    """Evaluate the model."""
    if not check_config():
        return
    
    print("Running evaluation...")
    report = evaluate_all_cases()
    print_evaluation_report(report)


def cmd_review_log() -> None:
    """Show human review log summary."""
    review = HumanReview()
    review.print_summary()
    
    corrected = review.list_corrected_cases()
    if corrected:
        print("\nCorrected Cases (Edited/Rejected):")
        for c in corrected:
            print(f"  Case {c['case_id']}: {c['title']} - {c['decision']}")
            print(f"    AI: {c['ai_fault']}")
            print(f"    Human: {c['corrected_fault']}")


def cmd_dashboard() -> None:
    """Generate and open HTML dashboard."""
    print("Generating dashboard...")
    dashboard_file = generate_dashboard()
    print(f"Dashboard saved to: {dashboard_file}")
    
    import webbrowser
    webbrowser.open(f"file://{dashboard_file}")
    print("Opened in browser.")


def cmd_rule_check() -> None:
    """Run rule checker on a specific case."""
    try:
        case_id_str = input("Enter case ID: ").strip()
        case_id = int(case_id_str)
    except ValueError:
        print("Invalid case ID")
        return
    
    evidence = load_evidence(case_id)
    if not evidence or evidence.is_empty():
        print(f"No evidence found for case {case_id}")
        return
    
    case = get_case(case_id)
    results = run_rule_checker(evidence, case)
    
    print(f"\nRule Checker Results for Case {case_id}:")
    if results:
        for r in results:
            print(f"  [{r['severity']}] {r['check']}: {r['message']}")
    else:
        print("  No issues found.")


def main() -> None:
    """Main CLI loop."""
    setup_logging()
    
    print("Cisco Network Troubleshooting AI - NetSage")
    print("Loading cases...")
    cases = load_cases()
    print(f"Loaded {len(cases)} cases")
    
    while True:
        print("\n" + "=" * 50)
        print("Cisco Network Troubleshooting AI")
        print("=" * 50)
        print("1. List cases")
        print("2. Diagnose a case")
        print("3. Validate dataset")
        print("4. Evaluate model")
        print("5. Human review log")
        print("6. Generate dashboard")
        print("7. Run rule checker")
        print("8. Exit")
        print()
        
        try:
            choice = input("Choice: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        
        if choice == "1":
            cmd_list_cases()
        elif choice == "2":
            cmd_diagnose()
        elif choice == "3":
            cmd_validate()
        elif choice == "4":
            cmd_evaluate()
        elif choice == "5":
            cmd_review_log()
        elif choice == "6":
            cmd_dashboard()
        elif choice == "7":
            cmd_rule_check()
        elif choice == "8":
            print("Goodbye!")
            break
        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()