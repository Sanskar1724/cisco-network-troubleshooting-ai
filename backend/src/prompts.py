"""Prompt templates for the Cisco Network Troubleshooting AI."""

from typing import List
from src.models import Case, Evidence


SYSTEM_PROMPT = """You are a Cisco Network Troubleshooting Assistant. Your job is to analyze network troubleshooting evidence and identify which of the 30 known fault categories is present.

RULES:
1. Analyze ONLY the provided evidence. Do not assume configurations not shown.
2. Match the fault to ONE of the 30 known cases provided.
3. Explain your diagnosis briefly, citing specific evidence.
4. Give a confidence score from 0.0 to 1.0.
5. Provide a practical Cisco fix with CLI commands when possible.
6. NEVER invent CLI output. NEVER claim a configuration exists unless evidence shows it.
7. If evidence is insufficient to distinguish between cases, set needs_more_evidence=true.
8. Do not guess just to produce an answer.

OUTPUT FORMAT (JSON only):
{
  "predicted_fault": "Case title from the known cases",
  "confidence": 0.95,
  "reasoning_summary": "Brief explanation citing specific evidence",
  "evidence_used": ["evidence1", "evidence2"],
  "recommended_fix": "Description of the fix",
  "commands": ["enable", "configure terminal", "..."],
  "needs_more_evidence": false
}"""


def build_case_list_prompt(cases: List[Case]) -> str:
    """Build a formatted list of candidate cases for the prompt."""
    lines = []
    for case in cases:
        lines.append(f"Case {case.case_id}: {case.title}")
        lines.append(f"  Expected Fault: {case.expected_fault}")
        lines.append(f"  Concept: {case.concept}")
        lines.append(f"  Severity: {case.severity}")
        lines.append("")
    return "\n".join(lines)


def build_diagnosis_prompt(evidence: Evidence, candidate_cases: List[Case]) -> str:
    """Build the complete diagnosis prompt for the LLM."""
    evidence_str = ""
    evidence_dict = evidence.to_dict()
    
    if evidence_dict:
        evidence_lines = ["TROUBLESHOOTING EVIDENCE:"]
        for key, value in evidence_dict.items():
            header = key.replace("_", " ").title()
            evidence_lines.append(f"\n=== {header} ===")
            evidence_lines.append(value)
        evidence_str = "\n".join(evidence_lines)
    else:
        evidence_str = "TROUBLESHOOTING EVIDENCE:\nNo evidence provided."
    
    cases_str = build_case_list_prompt(candidate_cases)
    
    return f"""{evidence_str}

KNOWN FAULT CATEGORIES (match to ONE):
{cases_str}

Analyze the evidence and identify the most likely fault. Return ONLY the JSON response.""" 


def build_evaluation_prompt(evidence: Evidence, candidate_cases: List[Case]) -> str:
    """Build prompt for evaluation mode (same as diagnosis)."""
    return build_diagnosis_prompt(evidence, candidate_cases)