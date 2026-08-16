"""Evaluation system for the Cisco Network Troubleshooting AI."""

import logging
from typing import List, Dict, Any
from src.models import Case, Evidence, DiagnosisResult
from src.data_loader import load_cases, get_case
from src.evidence_parser import load_evidence, create_all_placeholders
from src.diagnosis import diagnose, filter_candidate_cases

logger = logging.getLogger(__name__)


def evaluate_all_cases() -> Dict[str, Any]:
    """Evaluate the model against all cases with evidence files."""
    create_all_placeholders()
    
    cases = load_cases()
    results = []
    correct = 0
    total = 0
    
    for case in cases:
        evidence = load_evidence(case.case_id)
        if not evidence or evidence.is_empty():
            logger.info(f"Skipping case {case.case_id}: no evidence file")
            continue
        
        total += 1
        try:
            result = diagnose(evidence, case.case_id)
            is_correct = _compare_faults(result.predicted_fault, case.expected_fault)
            if is_correct:
                correct += 1
            
            results.append({
                "case_id": case.case_id,
                "title": case.title,
                "expected": case.expected_fault,
                "predicted": result.predicted_fault,
                "confidence": result.confidence,
                "correct": is_correct
            })
            logger.info(f"Case {case.case_id}: {'✓' if is_correct else '✗'} ({result.confidence:.2f})")
        except Exception as e:
            logger.error(f"Error evaluating case {case.case_id}: {e}")
            results.append({
                "case_id": case.case_id,
                "title": case.title,
                "expected": case.expected_fault,
                "predicted": f"ERROR: {e}",
                "confidence": 0.0,
                "correct": False
            })
    
    accuracy = correct / total if total > 0 else 0.0
    
    return {
        "total_evaluated": total,
        "correct": correct,
        "accuracy": accuracy,
        "results": results
    }


def _compare_faults(predicted: str, expected: str) -> bool:
    """Compare predicted fault with expected fault (case-insensitive, partial match)."""
    pred_lower = predicted.lower().strip()
    exp_lower = expected.lower().strip()
    return exp_lower in pred_lower or pred_lower in exp_lower


def print_evaluation_report(report: Dict[str, Any]) -> None:
    """Print a formatted evaluation report."""
    print("\n" + "=" * 60)
    print("MODEL EVALUATION REPORT")
    print("=" * 60)
    print(f"Total Evaluated: {report['total_evaluated']}")
    print(f"Correct Predictions: {report['correct']}")
    print(f"Accuracy: {report['accuracy']:.2%}")
    print()
    print("Case | Expected | Predicted | Correct")
    print("-" * 60)
    
    for r in report["results"]:
        status = "✓" if r["correct"] else "✗"
        predicted = r["predicted"][:40] + "..." if len(r["predicted"]) > 40 else r["predicted"]
        expected = r["expected"][:40] + "..." if len(r["expected"]) > 40 else r["expected"]
        print(f"{r['case_id']:4} | {expected} | {predicted} | {status}")