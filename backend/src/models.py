"""Pydantic models for the Cisco Network Troubleshooting AI."""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class Severity(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class Case(BaseModel):
    """Represents a network troubleshooting case from the CSV dataset."""
    case_id: int
    title: str
    topology: str
    symptom: str
    topology_note: str
    show_outputs: str
    expected_fault: str
    osi_layer: str
    concept: str
    severity: Severity

    class Config:
        use_enum_values = True


class Evidence(BaseModel):
    """Structured troubleshooting evidence provided by the user."""
    case_id: Optional[int] = None
    user_description: str = ""
    ping_results: str = ""
    ipconfig: str = ""
    show_ip_interface_brief: str = ""
    show_running_config: str = ""
    show_vlan_brief: str = ""
    show_interfaces_trunk: str = ""
    show_ip_route: str = ""
    show_access_lists: str = ""
    show_ip_nat_translations: str = ""
    other_cli_output: str = ""

    def to_dict(self) -> Dict[str, str]:
        """Convert evidence to dictionary, excluding empty fields."""
        return {k: v for k, v in self.model_dump().items() if v and k != "case_id"}

    def is_empty(self) -> bool:
        """Check if all evidence fields are empty."""
        return all(not v for k, v in self.model_dump().items() if k != "case_id")


class DiagnosisResult(BaseModel):
    """Structured diagnosis result from the AI."""
    case_id: int
    predicted_fault: str
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning_summary: str
    evidence_used: List[str]
    recommended_fix: str
    commands: List[str]
    needs_more_evidence: bool

    class Config:
        use_enum_values = True


class CandidateCase(BaseModel):
    """A case that matches the evidence keywords."""
    case: Case
    match_reason: str