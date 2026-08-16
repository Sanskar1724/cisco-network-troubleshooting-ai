# GitHub Push Strategy - NetSage AI

## Overview
Divide the project into **4 logical pushes** with atomic, meaningful commits.

---

## Part 1: Foundation & Core Data Layer
**Branch:** `part1-foundation`  
**Push:** `git push origin part1-foundation`  
**PR Title:** `feat: Foundation - Project structure, data models, CSV loader, validation`

### Files Included
```
backend/
├── .gitignore
├── .env.example
├── requirements.txt
├── main_cli.py                 # CLI entry point (8 commands)
├── src/
│   ├── __init__.py
│   ├── config.py               # .env loading, paths, constants
│   ├── models.py               # Pydantic: Case, Evidence, DiagnosisResult
│   ├── data_loader.py          # CSV load, validate, query
│   ├── evidence_parser.py      # Parse evidence files, create templates
│   └── utils.py                # CLI helpers, logging
├── data/
│   ├── cases.csv               # 30 cases (SOURCE OF TRUTH)
│   └── evidence/               # 30 evidence files (case_01-30.txt)
├── tests/
│   ├── __init__.py
│   └── test_data_loader.py     # 5 tests
├── scripts/
│   └── validate.py             # Standalone validation script
└── docs/
    └── README.md               # Main documentation (copied from root)
```

### Commits (4-5 commits)

| Commit | Message |
|--------|---------|
| 1 | `chore: init project structure with .gitignore, .env.example, requirements.txt` |
| 2 | `feat: add core data models (Case, Evidence, DiagnosisResult) with Pydantic` |
| 3 | `feat: implement CSV data loader with validation (30 cases, 10 checks)` |
| 4 | `feat: add evidence parser with structured section parsing` |
| 5 | `test: add data_loader tests (5 tests passing)` |

---

## Part 2: Rule Checker & Diagnosis Pipeline
**Branch:** `part2-pipeline` (from `part1-foundation`)  
**Push:** `git push origin part2-pipeline`  
**PR Title:** `feat: Rule checker (10 checks) + Diagnosis pipeline (Rules → Filter → LLM)`

### Files Added/Modified
```
backend/
├── src/
│   ├── rule_checker.py         # 10 deterministic checks
│   ├── diagnosis.py            # Pipeline: Rules → Filter → LLM → Result
│   ├── prompts.py              # System prompt + worked examples
│   └── llm_client.py           # OpenRouter + fallback chain
├── diagnose_prompt.md          # System prompt + 3 worked examples
├── tests/
│   ├── test_diagnosis.py       # 5 tests
│   └── test_evaluator.py       # 5 tests
└── scripts/
    └── test_integration.py     # Integration test
```

### Commits (4-5 commits)

| Commit | Message |
|--------|---------|
| 1 | `feat: add rule checker with 10 deterministic checks (subnet, gateway, VLAN, DHCP, ACL, NAT)` |
| 2 | `feat: implement diagnosis pipeline (Rule Checker → Keyword Filter → LLM)` |
| 3 | `feat: add LLM client with fallback chain (Gemma 4 → auto)` |
| 4 | `feat: add prompt library with system prompt + 3 worked examples` |
| 5 | `test: add diagnosis & evaluator tests (10 tests passing)` |

---

## Part 3: Human Review, Dashboard & Evaluation
**Branch:** `part3-review-dashboard` (from `part2-pipeline`)  
**Push:** `git push origin part3-review-dashboard`  
**PR Title:** `feat: Human review workflow (Accepted/Edited/Rejected) + HTML Dashboard + Evaluation`

### Files Added/Modified
```
backend/
├── src/
│   ├── human_review.py         # Accepted/Edited/Rejected workflow + Markdown log
│   ├── dashboard.py            # HTML + Chart.js dashboard generator
│   └── evaluator.py            # Batch evaluation with accuracy metrics
├── data/
│   ├── human_review_log.md     # Append-only review log
│   └── dashboard.html          # Generated HTML dashboard
├── tests/
│   └── (all 15 tests pass)
├── docs/
│   ├── INDEX.md                # Documentation hub
│   ├── ARCHITECTURE.md         # System design
│   ├── API_REFERENCE.md        # Complete API docs
│   ├── VSCODE_SETUP.md         # IDE configuration
│   ├── TESTING.md              # Testing guide
│   └── TROUBLESHOOTING.md      # Common issues
└── main_cli.py                 # Updated with review, dashboard, rule-check commands
```

### Commits (5-6 commits)

| Commit | Message |
|--------|---------|
| 1 | `feat: add human review workflow (Accepted/Edited/Rejected + Markdown log)` |
| 2 | `feat: add HTML dashboard with Chart.js (stats, charts, tables, review log)` |
| 3 | `feat: add evaluation system (batch accuracy, per-case results)` |
| 4 | `docs: add complete documentation (Architecture, API, Testing, VS Code, Troubleshooting)` |
| 5 | `feat: update CLI with review log, dashboard generation, rule check commands` |
| 6 | `chore: update main_cli.py with all 8 commands integrated` |

---

## Part 4: FastAPI Server + Frontend Web UI
**Branch:** `part4-web-api` (from `part3-review-dashboard`)  
**Push:** `git push origin part4-web-api`  
**PR Title:** `feat: FastAPI server + Web UI (5 pages) + REST API (15 endpoints) + WebSocket`

### Files Added/Modified
```
backend/
├── main.py                     # FastAPI server (uvicorn)
├── frontend/
│   ├── static/
│   │   ├── css/style.css       # Custom styles (Bootstrap 5)
│   │   ├── js/main.js          # Main JS (API calls, toasts, forms)
│   │   └── data/               # Static data files
│   └── templates/
│       ├── base.html           # Base template with navbar
│       ├── index.html          # Home page with stats
│       ├── diagnose.html       # Diagnosis page (evidence + rule checker + AI + review)
│       ├── cases.html          # All cases table (search, filter, modals)
│       ├── review.html         # Review log with stats + corrected cases
│       └── dashboard.html      # Dashboard with Chart.js + tables
├── docs/
│   └── FULL_DOCS.md            # Complete documentation (optional)
├── tests/
│   └── (all 15 tests + API tests)
└── .vscode/                    # VS Code configs (settings, launch, tasks, snippets)
```

### Commits (6-7 commits)

| Commit | Message |
|--------|---------|
| 1 | `feat: add FastAPI server with lifespan, static files, Jinja2 templates` |
| 2 | `feat: implement 5 web pages (Home, Dashboard, Diagnose, Cases, Review)` |
| 3 | `feat: add 15 REST API endpoints (diagnose, rule-check, review, dashboard, evaluate)` |
| 4 | `feat: add WebSocket support for real-time diagnosis updates` |
| 4 | `feat: add responsive CSS + vanilla JS (API calls, toasts, modals, charts)` |
| 5 | `feat: add Chart.js integration (doughnut + bar charts) to dashboard` |
| 6 | `feat: add VS Code configs (settings, launch, tasks, snippets)` |
| 7 | `chore: fix TemplateResponse signature for Starlette/FastAPI compatibility` |

---

## Final Merge Strategy

```bash
# 1. Create main branch from part4
git checkout -b main part4-web-api

# 2. Push main
git push origin main

# 3. Tag release
git tag -a v1.0.0 -m "v1.0.0: NetSage AI - Complete with CLI, Web UI, API, Dashboard, Human Review"
git push origin v1.0.0

# 4. Clean up feature branches (optional)
git branch -d part1-foundation part2-pipeline part3-review-dashboard part4-web-api
git push origin --delete part1-foundation part2-pipeline part3-review-dashboard part4-web-api
```

---

## Commit Message Convention

```
<type>(<scope>): <subject>

<body>

<footer>
```

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `chore` | Maintenance, deps, config |
| `docs` | Documentation only |
| `test` | Adding tests |
| `refactor` | Code restructuring |
| `style` | Formatting, linting |

---

## Pre-Push Checklist

- [ ] All 15 tests pass: `$env:PYTHONPATH="."; pytest tests/ -v`
- [ ] CLI works: `python main_cli.py` (all 8 commands)
- [ ] Web server starts: `python main.py` → http://127.0.0.1:8000
- [ ] All 5 pages load (Home, Dashboard, Diagnose, Cases, Review)
- [ ] API endpoints respond (health, cases, diagnose, review, dashboard)
- [ ] Dashboard generates: `python main_cli.py` → Option 6
- [ ] Review log works: `python main_cli.py` → Option 5
- [ ] Evidence files exist: `data/evidence/case_01.txt` through `case_30.txt`
- [ ] `.env` not committed (check .gitignore)
- [ ] No `__pycache__`, `.pytest_cache`, `.venv` in repo