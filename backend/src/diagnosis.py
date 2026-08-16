"""Diagnosis engine for the Cisco Network Troubleshooting AI."""

import logging
from typing import List, Optional
from src.models import Case, Evidence, DiagnosisResult, CandidateCase
from src.data_loader import load_cases, get_case
from src.evidence_parser import normalize_evidence
from src.prompts import SYSTEM_PROMPT, build_diagnosis_prompt
from src.llm_client import create_llm_client
from src.rule_checker import run_rule_checker

logger = logging.getLogger(__name__)


CONCEPT_KEYWORDS = {
    "IP Addressing": ["ip address", "ipconfig", "wrong ip", "wrong network"],
    "Subnet Mask": ["subnet mask", "netmask", "255.255"],
    "Default Gateway": ["default gateway", "gateway", "0.0.0.0"],
    "Interface Status": ["interface", "shutdown", "administratively down", "up down"],
    "VLAN": ["vlan", "access vlan", "switchport access", "vlan 10", "vlan 20"],
    "VLAN Trunking": ["trunk", "switchport mode trunk", "allowed vlan", "encapsulation dot1q"],
    "Inter-VLAN Routing": ["inter-vlan", "subinterface", "g0/0.", "router-on-a-stick", "encapsulation"],
    "DHCP": ["dhcp", "ip dhcp pool", "default-router", "169.254", "dhcp pool"],
    "Routing": ["ip route", "static route", "show ip route", "missing route", "next hop"],
    "Router Interface": ["gigabitethernet", "interface down", "administratively down"],
    "DNS": ["dns", "nameserver", "domain name", "resolution", "nslookup"],
    "ACL": ["access-list", "access-group", "permit", "deny", "acl"],
    "NAT": ["ip nat", "inside", "outside", "nat pool", "overload"],
    "Wireless Networking": ["wireless", "wifi", "ssid", "wpa", "authentication"],
    "Wireless / Internal Server Connectivity": ["wireless", "internal server", "wired server"],
}


def filter_candidate_cases(evidence: Evidence, all_cases: List[Case]) -> List[CandidateCase]:
    """Filter cases based on keywords in the evidence."""
    evidence_text = normalize_evidence(evidence).lower()
    
    if not evidence_text.strip() or evidence_text == "no evidence provided.":
        return [CandidateCase(case=c, match_reason="No evidence - all cases considered") for c in all_cases]
    
    matched_concepts = set()
    for concept, keywords in CONCEPT_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in evidence_text:
                matched_concepts.add(concept)
                break
    
    candidates = []
    for case in all_cases:
        match_reason = ""
        if case.concept in matched_concepts:
            match_reason = f"Evidence matches concept: {case.concept}"
        elif any(kw in evidence_text for kw in CONCEPT_KEYWORDS.get(case.concept, [])):
            match_reason = f"Keyword match for concept: {case.concept}"
        
        if match_reason:
            candidates.append(CandidateCase(case=case, match_reason=match_reason))
    
    if not candidates:
        logger.warning("No candidate cases matched, returning all cases")
        return [CandidateCase(case=c, match_reason="No keyword match - fallback to all cases") for c in all_cases]
    
    return candidates


def diagnose(evidence: Evidence, case_id: Optional[int] = None) -> DiagnosisResult:
    """Run the diagnosis pipeline: Rule Checker -> LLM -> Result."""
    logger.info(f"Starting diagnosis for case_id={case_id}")
    
    all_cases = load_cases()
    
    if case_id:
        target_case = get_case(case_id)
        if not target_case:
            raise ValueError(f"Case {case_id} not found")
        candidate_cases = [CandidateCase(case=target_case, match_reason=f"User specified case {case_id}")]
    else:
        candidate_cases = filter_candidate_cases(evidence, all_cases)
    
    logger.info(f"Candidate cases: {[c.case.case_id for c in candidate_cases]}")
    
    # Run deterministic rule checker first
    rule_results = run_rule_checker(evidence, candidate_cases[0].case if candidate_cases else None)
    if rule_results:
        logger.info(f"Rule checker found {len(rule_results)} issues")
        for r in rule_results:
            logger.warning(f"  {r['check']}: {r['message']}")
    
    llm_client = create_llm_client()
    prompt = build_diagnosis_prompt(evidence, [c.case for c in candidate_cases])
    
    response = llm_client.diagnose(SYSTEM_PROMPT, prompt)
    
    result = DiagnosisResult(
        case_id=case_id or 0,
        predicted_fault=response.get("predicted_fault", "Unknown"),
        confidence=float(response.get("confidence", 0.0)),
        reasoning_summary=response.get("reasoning_summary", ""),
        evidence_used=response.get("evidence_used", []),
        recommended_fix=response.get("recommended_fix", ""),
        commands=response.get("commands", []),
        needs_more_evidence=bool(response.get("needs_more_evidence", False))
    )
    
    logger.info(f"Diagnosis complete: {result.predicted_fault} (confidence: {result.confidence})")
    return result


def format_diagnosis(result: DiagnosisResult) -> str:
    """Format a diagnosis result for display."""
    lines = [
        "=" * 40,
        "NETWORK TROUBLESHOOTING DIAGNOSIS",
        "=" * 40,
        "",
        f"Predicted Case:",
        f"{result.predicted_fault}",
        "",
        f"Confidence:",
        f"{result.confidence:.2f}",
        "",
        f"Diagnosis:",
        f"{result.reasoning_summary}",
        "",
        f"Evidence:",
    ]
    
    for ev in result.evidence_used:
        lines.append(f"- {ev}")
    
    lines.extend([
        "",
        f"Recommended Fix:",
        f"{result.recommended_fix}",
        "",
        f"Commands:",
    ])
    
    for cmd in result.commands:
        lines.append(cmd)
    
    lines.extend([
        "",
        f"Needs More Evidence:",
        f"{'Yes' if result.needs_more_evidence else 'No'}",
    ])
    
    return "\n".join(lines)