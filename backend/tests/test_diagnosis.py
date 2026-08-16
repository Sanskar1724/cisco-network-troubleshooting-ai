"""Tests for diagnosis module."""

import pytest
from src.diagnosis import filter_candidate_cases, diagnose
from src.data_loader import load_cases
from src.models import Evidence
from src.evidence_parser import normalize_evidence


def test_filter_candidate_cases_dhcp():
    cases = load_cases()
    evidence = Evidence(
        case_id=14,
        ipconfig="IP Address: 192.168.10.5\nDefault Gateway: 192.168.10.254",
        show_running_config="ip dhcp pool LAN1\n network 192.168.10.0 255.255.255.0\n default-router 192.168.10.254"
    )
    candidates = filter_candidate_cases(evidence, cases)
    assert len(candidates) > 0
    concepts = [c.case.concept for c in candidates]
    assert any("DHCP" in c for c in concepts)


def test_filter_candidate_cases_vlan():
    cases = load_cases()
    evidence = Evidence(
        case_id=5,
        show_vlan_brief="VLAN 20 only\nVLAN 10 missing",
        show_running_config="interface FastEthernet0/1\n switchport access vlan 10"
    )
    candidates = filter_candidate_cases(evidence, cases)
    assert len(candidates) > 0
    concepts = [c.case.concept for c in candidates]
    assert any("VLAN" in c for c in concepts)


def test_filter_candidate_cases_empty_evidence():
    cases = load_cases()
    evidence = Evidence()
    candidates = filter_candidate_cases(evidence, cases)
    assert len(candidates) == 30


def test_normalize_evidence():
    evidence = Evidence(
        ipconfig="IP: 192.168.1.1",
        ping_results="Reply from 192.168.1.2"
    )
    normalized = normalize_evidence(evidence)
    assert "IP: 192.168.1.1" in normalized
    assert "Reply from 192.168.1.2" in normalized


def test_diagnosis_result_validation():
    from src.models import DiagnosisResult
    result = DiagnosisResult(
        case_id=1,
        predicted_fault="Wrong IP Address",
        confidence=0.95,
        reasoning_summary="Test",
        evidence_used=["test"],
        recommended_fix="Fix it",
        commands=["cmd1"],
        needs_more_evidence=False
    )
    assert result.confidence == 0.95
    assert result.needs_more_evidence is False
    
    with pytest.raises(ValueError):
        DiagnosisResult(
            case_id=1,
            predicted_fault="Test",
            confidence=1.5,
            reasoning_summary="Test",
            evidence_used=[],
            recommended_fix="Test",
            commands=[],
            needs_more_evidence=False
        )