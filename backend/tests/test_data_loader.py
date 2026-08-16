"""Tests for data_loader module."""

import pytest
from src.data_loader import load_cases, get_case, get_cases_by_concept, get_cases_by_title, validate_dataset
from src.models import Case


def test_load_cases():
    cases = load_cases()
    assert len(cases) == 30
    assert all(isinstance(c, Case) for c in cases)
    assert all(1 <= c.case_id <= 30 for c in cases)


def test_get_case():
    case = get_case(1)
    assert case is not None
    assert case.case_id == 1
    assert case.title == "Wrong IP Address"
    
    assert get_case(999) is None


def test_get_cases_by_concept():
    cases = get_cases_by_concept("DHCP")
    assert len(cases) >= 4
    assert all("DHCP" in c.concept for c in cases)


def test_get_cases_by_title():
    cases = get_cases_by_title("Wrong IP")
    assert len(cases) >= 1
    assert any("Wrong IP" in c.title for c in cases)


def test_validate_dataset():
    report = validate_dataset()
    assert "total_cases" in report
    assert "status" in report
    assert report["total_cases"] == 30
    assert report["required_columns"] is True
    assert report["duplicate_ids"] is True
    assert report["missing_titles"] is True
    assert report["missing_concepts"] is True
    assert report["missing_severities"] is True