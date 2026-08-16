"""Tests for evaluator module."""

import pytest
from src.evaluator import _compare_faults


def test_compare_faults_exact_match():
    assert _compare_faults("Wrong IP Address", "Wrong IP Address") is True


def test_compare_faults_case_insensitive():
    assert _compare_faults("wrong ip address", "Wrong IP Address") is True
    assert _compare_faults("WRONG IP ADDRESS", "Wrong IP Address") is True


def test_compare_faults_partial_match():
    assert _compare_faults("Case 1: Wrong IP Address", "Wrong IP Address") is True
    assert _compare_faults("Wrong IP Address", "Case 1: Wrong IP Address") is True


def test_compare_faults_no_match():
    assert _compare_faults("Wrong Subnet Mask", "Wrong IP Address") is False
    assert _compare_faults("DHCP Pool Missing", "Wrong DHCP Gateway") is False


def test_compare_faults_substring():
    assert _compare_faults("The fault is Wrong IP Address on PC1", "Wrong IP Address") is True
    assert _compare_faults("Wrong IP Address", "The fault is Wrong IP Address on PC1") is True