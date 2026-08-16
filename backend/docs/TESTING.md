# Testing Guide

## Test Structure

```
backend/tests/
├── test_data_loader.py    # 5 tests
├── test_diagnosis.py      # 5 tests
└── test_evaluator.py      # 5 tests
```

---

## Running Tests

### All Tests
```bash
cd backend
$env:PYTHONPATH="."; pytest tests/ -v
```

### Specific Test File
```bash
pytest tests/test_data_loader.py -v
pytest tests/test_diagnosis.py -v
pytest tests/test_evaluator.py -v
```

### Specific Test
```bash
pytest tests/test_diagnosis.py::test_filter_candidate_cases_dhcp -v
```

### With Coverage
```bash
pytest tests/ --cov=src --cov-report=html --cov-report=term
```

### Parallel Execution
```bash
pytest tests/ -n auto
```

---

## Test Categories

### Data Loader Tests (`test_data_loader.py`)

| Test | Purpose |
|------|---------|
| `test_load_cases` | Loads all 30 cases correctly |
| `test_get_case` | Retrieves single case by ID |
| `test_get_cases_by_concept` | Filters by concept (e.g., "DHCP") |
| `test_get_cases_by_title` | Filters by title keyword |
| `test_validate_dataset` | Full CSV validation |

### Diagnosis Tests (`test_diagnosis.py`)

| Test | Purpose |
|------|---------|
| `test_filter_candidate_cases_dhcp` | DHCP keywords → cases 12-15 |
| `test_filter_candidate_cases_vlan` | VLAN keywords → cases 5-11 |
| `test_filter_candidate_cases_empty_evidence` | Empty evidence → all 30 cases |
| `test_normalize_evidence` | Evidence → formatted string |
| `test_diagnosis_result_validation` | Pydantic validation |

### Evaluator Tests (`test_evaluator.py`)

| Test | Purpose |
|------|---------|
| `test_compare_faults_exact_match` | Exact string match |
| `test_compare_faults_case_insensitive` | Case insensitive |
| `test_compare_faults_partial_match` | Substring match |
| `test_compare_faults_no_match` | Different faults |
| `test_compare_faults_substring` | Both directions |

---

## Integration Tests

```bash
# Run integration test
python scripts/test_integration.py
```

Tests:
- Rule checker on case 1
- AI diagnosis on case 1
- Dashboard generation

---

## Test Coverage

```bash
# Generate coverage report
pytest tests/ --cov=src --cov-report=html --cov-report=term

# View HTML report
open htmlcov/index.html
```

**Target**: >80% coverage on `src/` modules

---

## CI/CD Pipeline (GitHub Actions Example)

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd backend
          $env:PYTHONPATH="."; pytest tests/ -v
      - name: Lint
        run: |
          cd backend
          pip install black pylint
          black --check src/ tests/ main.py main_cli.py
          pylint src/ main.py main_cli.py
      - name: Type check
        run: |
          cd backend
          pip install mypy
          mypy src/
```

---

## Debugging Tests

### Debug Specific Test
```bash
# With VS Code debugger
# Set breakpoint in test file
# Press F5 → "Pytest: Current File"
```

### Verbose Output
```bash
pytest tests/ -v -s  # -s shows print statements
```

### Stop on First Failure
```bash
pytest tests/ -x
```

### Run Failed Tests Only
```bash
pytest tests/ --lf
```

---

## Mocking External Services

```python
# tests/conftest.py
import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def mock_llm_client():
    with patch('src.diagnosis.create_llm_client') as mock:
        client = Mock()
        client.diagnose.return_value = {
            "predicted_fault": "Wrong IP Address",
            "confidence": 0.95,
            "reasoning_summary": "Test reasoning",
            "evidence_used": ["test evidence"],
            "recommended_fix": "Test fix",
            "commands": ["test command"],
            "needs_more_evidence": False
        }
        mock.return_value = client
        yield client
```

---

## Performance Testing

```bash
# Time test execution
pytest tests/ --durations=10

# Profile
pytest tests/ --profile --profile-svg=profile.svg
```

---

## Test Data Management

| File | Purpose |
|------|---------|
| `data/cases.csv` | 30 ground truth cases |
| `data/evidence/case_XX.txt` | Evidence per case |
| `data/human_review_log.md` | Human review audit trail |

**Rule**: Never modify `cases.csv` - it's the source of truth.

---

## Troubleshooting Tests

| Issue | Solution |
|------|----------|
| `ModuleNotFoundError: src` | `$env:PYTHONPATH="."; pytest tests/` |
| Import errors | Ensure `.venv` activated, deps installed |
| Flaky tests | Check for shared state, use fixtures |
| Slow tests | Use `--durations=10` to identify |
| LLM rate limits | Mock `create_llm_client` in tests |