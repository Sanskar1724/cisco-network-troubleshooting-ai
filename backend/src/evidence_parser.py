"""Evidence parsing and normalization for the Cisco Network Troubleshooting AI."""

from pathlib import Path
from typing import Optional
from src.config import EVIDENCE_DIR
from src.models import Evidence


def load_evidence(case_id: int) -> Optional[Evidence]:
    """Load evidence from a case file."""
    evidence_file = EVIDENCE_DIR / f"case_{case_id:02d}.txt"
    if not evidence_file.exists():
        return None
    
    content = evidence_file.read_text(encoding="utf-8")
    return parse_evidence_file(content, case_id)


def parse_evidence_file(content: str, case_id: int) -> Evidence:
    """Parse a structured evidence file into an Evidence object."""
    evidence = Evidence(case_id=case_id)
    
    sections = {
        "user_description": "user_description",
        "ping_results": "ping_results",
        "ipconfig": "ipconfig",
        "show_ip_interface_brief": "show_ip_interface_brief",
        "show_running_config": "show_running_config",
        "show_vlan_brief": "show_vlan_brief",
        "show_interfaces_trunk": "show_interfaces_trunk",
        "show_ip_route": "show_ip_route",
        "show_access_lists": "show_access_lists",
        "show_ip_nat_translations": "show_ip_nat_translations",
        "other_cli_output": "other_cli_output",
    }
    
    current_section = None
    current_content = []
    
    for line in content.splitlines():
        line_lower = line.lower().strip()
        matched_section = None
        
        for key, attr in sections.items():
            if line_lower.startswith(f"[{key}]") or line_lower.startswith(f"=== {key} ==="):
                matched_section = attr
                break
        
        if matched_section:
            if current_section and current_content:
                setattr(evidence, current_section, "\n".join(current_content).strip())
            current_section = matched_section
            current_content = []
        else:
            current_content.append(line)
    
    if current_section and current_content:
        setattr(evidence, current_section, "\n".join(current_content).strip())
    
    return evidence


def create_placeholder_evidence(case_id: int) -> None:
    """Create a placeholder evidence file for a case."""
    evidence_file = EVIDENCE_DIR / f"case_{case_id:02d}.txt"
    if evidence_file.exists():
        return
    
    template = f"""[user_description]
EVIDENCE NOT COLLECTED YET

[ping_results]
EVIDENCE NOT COLLECTED YET

[ipconfig]
EVIDENCE NOT COLLECTED YET

[show_ip_interface_brief]
EVIDENCE NOT COLLECTED YET

[show_running_config]
EVIDENCE NOT COLLECTED YET

[show_vlan_brief]
EVIDENCE NOT COLLECTED YET

[show_interfaces_trunk]
EVIDENCE NOT COLLECTED YET

[show_ip_route]
EVIDENCE NOT COLLECTED YET

[show_access_lists]
EVIDENCE NOT COLLECTED YET

[show_ip_nat_translations]
EVIDENCE NOT COLLECTED YET

[other_cli_output]
EVIDENCE NOT COLLECTED YET
"""
    evidence_file.write_text(template, encoding="utf-8")


def create_all_placeholders() -> None:
    """Create placeholder evidence files for all 30 cases."""
    for i in range(1, 31):
        create_placeholder_evidence(i)


def normalize_evidence(evidence: Evidence) -> str:
    """Convert Evidence object to a formatted string for the LLM."""
    parts = []
    evidence_dict = evidence.to_dict()
    
    for key, value in evidence_dict.items():
        if value:
            header = key.replace("_", " ").title()
            parts.append(f"=== {header} ===\n{value}\n")
    
    return "\n".join(parts) if parts else "No evidence provided."