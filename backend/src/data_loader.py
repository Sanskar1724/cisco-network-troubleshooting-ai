"""Data loading and validation for the Cisco Network Troubleshooting AI."""

import pandas as pd
from pathlib import Path
from typing import List, Optional, Dict, Any
from src.config import CASES_CSV
from src.models import Case, Severity


def load_cases() -> List[Case]:
    """Load all cases from the CSV file."""
    df = pd.read_csv(CASES_CSV)
    cases = []
    for _, row in df.iterrows():
        case = _row_to_case(row)
        if case:
            cases.append(case)
    return cases


def _row_to_case(row: pd.Series) -> Optional[Case]:
    """Convert a DataFrame row to a Case object."""
    try:
        case_id = int(row.iloc[0])
        expected_fault = str(row["expected_fault"]) if pd.notna(row["expected_fault"]) else ""
        
        if not expected_fault and case_id == 11:
            show_outputs = str(row["show_outputs"]) if pd.notna(row["show_outputs"]) else ""
            if "expected_fault:" in show_outputs.lower():
                idx = show_outputs.lower().index("expected_fault:")
                expected_fault = show_outputs[idx + len("expected_fault:"):].strip()
        
        severity_str = str(row["severity"]).strip().capitalize()
        try:
            severity = Severity(severity_str)
        except ValueError:
            severity = Severity.MEDIUM
        
        return Case(
            case_id=case_id,
            title=str(row["title"]).strip(),
            topology=str(row["topology"]).strip(),
            symptom=str(row["symptom"]).strip() if pd.notna(row["symptom"]) else "",
            topology_note=str(row["topology_note"]).strip() if pd.notna(row["topology_note"]) else "",
            show_outputs=str(row["show_outputs"]).strip() if pd.notna(row["show_outputs"]) else "",
            expected_fault=expected_fault.strip(),
            osi_layer=str(row["osi_layer"]).strip() if pd.notna(row["osi_layer"]) else "",
            concept=str(row["concept"]).strip() if pd.notna(row["concept"]) else "",
            severity=severity
        )
    except Exception as e:
        print(f"Error parsing case {row.iloc[0]}: {e}")
        return None


def get_case(case_id: int) -> Optional[Case]:
    """Retrieve a single case by ID."""
    cases = load_cases()
    for case in cases:
        if case.case_id == case_id:
            return case
    return None


def get_cases_by_concept(concept: str) -> List[Case]:
    """Retrieve cases matching a concept (case-insensitive partial match)."""
    cases = load_cases()
    concept_lower = concept.lower()
    return [c for c in cases if concept_lower in c.concept.lower()]


def get_cases_by_title(title: str) -> List[Case]:
    """Retrieve cases matching a title (case-insensitive partial match)."""
    cases = load_cases()
    title_lower = title.lower()
    return [c for c in cases if title_lower in c.title.lower()]


def validate_dataset() -> Dict[str, Any]:
    """Validate the dataset and return a validation report."""
    df = pd.read_csv(CASES_CSV)
    cases = load_cases()
    
    report = {
        "total_cases": len(cases),
        "required_columns": True,
        "duplicate_ids": True,
        "missing_titles": True,
        "missing_expected_faults": True,
        "missing_concepts": True,
        "missing_severities": True,
        "case_ids_range": True,
        "issues": []
    }
    
    required_columns = ["case_id", "title", "topology", "symptom", "topology_note",
                       "show_outputs", "expected_fault", "osi_layer", "concept", "severity"]
    missing_cols = [c for c in required_columns if c not in df.columns]
    if missing_cols:
        report["required_columns"] = False
        report["issues"].append(f"Missing columns: {missing_cols}")
    
    case_ids = [c.case_id for c in cases]
    if len(case_ids) != len(set(case_ids)):
        report["duplicate_ids"] = False
        report["issues"].append("Duplicate case IDs found")
    
    if set(case_ids) != set(range(1, 31)):
        report["case_ids_range"] = False
        missing = set(range(1, 31)) - set(case_ids)
        report["issues"].append(f"Missing case IDs: {sorted(missing)}")
    
    missing_titles = [c.case_id for c in cases if not c.title]
    if missing_titles:
        report["missing_titles"] = False
        report["issues"].append(f"Missing titles for cases: {missing_titles}")
    
    missing_faults = [c.case_id for c in cases if not c.expected_fault]
    if missing_faults:
        report["missing_expected_faults"] = False
        report["issues"].append(f"Missing expected_fault for cases: {missing_faults}")
    
    missing_concepts = [c.case_id for c in cases if not c.concept]
    if missing_concepts:
        report["missing_concepts"] = False
        report["issues"].append(f"Missing concepts for cases: {missing_concepts}")
    
    missing_severities = [c.case_id for c in cases if not c.severity]
    if missing_severities:
        report["missing_severities"] = False
        report["issues"].append(f"Missing severities for cases: {missing_severities}")
    
    all_pass = all([
        report["required_columns"],
        report["duplicate_ids"],
        report["missing_titles"],
        report["missing_expected_faults"],
        report["missing_concepts"],
        report["missing_severities"],
        report["case_ids_range"]
    ])
    report["status"] = "VALID" if all_pass else "INVALID"
    
    return report


def print_validation_report(report: Dict[str, Any]) -> None:
    """Print a formatted validation report."""
    print("\nDataset validation")
    print("-" * 40)
    print(f"Cases: {report['total_cases']}")
    print(f"Required columns: {'PASS' if report['required_columns'] else 'FAIL'}")
    print(f"Duplicate IDs: {'PASS' if report['duplicate_ids'] else 'FAIL'}")
    print(f"Missing titles: {'PASS' if report['missing_titles'] else 'FAIL'}")
    print(f"Missing expected faults: {'PASS' if report['missing_expected_faults'] else 'FAIL'}")
    print(f"Missing concepts: {'PASS' if report['missing_concepts'] else 'FAIL'}")
    print(f"Missing severities: {'PASS' if report['missing_severities'] else 'FAIL'}")
    print(f"Case IDs 1-30: {'PASS' if report['case_ids_range'] else 'FAIL'}")
    print(f"Status: {report['status']}")
    if report["issues"]:
        print("\nIssues:")
        for issue in report["issues"]:
            print(f"  - {issue}")