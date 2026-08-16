# GitHub Push Strategy - 4 Part Push Guide

## Overview
Push the project in **4 sequential parts** to main branch. Each part is a logical module with atomic commits.

**Remote:** `https://github.com/Sanskar1724/NetSage-AI.git`  
**Strategy:** Create feature branch → Add files → Commit with proper messages → Push → Merge to main

---

## Part 1: Foundation & Core Data Layer
**Most Important** - Core data models, CSV loader, evidence parser, validation

### Files to Add
```
backend/
├── .gitignore
├── .env.example
├── requirements.txt
├── main_cli.py
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── models.py
│   ├── data_loader.py
│   ├── evidence_parser.py
│   └── utils.py
├── data/
│   ├── cases.csv
│   └── evidence/case_01.txt ... case_30.txt
├── tests/
│   └── test_data_loader.py
├── scripts/
│   └── validate.py
└── docs/
    └── README.md
```

### Commands
```bash
# Create branch
git checkout -b part1-foundation

# Add files
git add backend/.gitignore backend/.env.example backend/requirements.txt backend/main_cli.py
git add backend/src/__init__.py backend/src/config.py backend/src/models.py backend/src/data_loader.py backend/src/evidence_parser.py backend/src/utils.py
git add backend/data/cases.csv backend/data/evidence/
git add backend/tests/test_data_loader.py backend/scripts/validate.py backend/docs/README.md

# Commit 1
git commit -m "chore: init project structure with .gitignore, .env.example, requirements.txt"

# Commit 2
git commit -m "feat: add core data models (Case, Evidence, DiagnosisResult) with Pydantic"

# Commit 3
git commit -m "feat: implement CSV data loader with validation (30 cases, 10 checks)"

# Commit 4
git commit -m "feat: add evidence parser with structured section parsing"

# Commit 5
git commit -m "test: add data_loader tests (5 tests passing)"

# Push
git push origin part1-foundation
```

---

## Part 2: Rule Checker & Diagnosis Pipeline
**Core Logic** - 10 deterministic checks + AI pipeline

### Files to Add
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

### Commands
```bash
# Create branch from part1
git checkout part1-foundation
git checkout -b part2-pipeline

# Add files
git add backend/src/rule_checker.py backend/src/diagnosis.py backend/src/prompts.py backend/src/llm_client.py
git add backend/diagnose_prompt.md backend/tests/test_diagnosis.py backend/tests/test_evaluator.py
git add backend/scripts/test_integration.py

# Commit 1
git commit -m "feat: add rule checker with 10 deterministic checks (subnet, gateway, VLAN, DHCP, ACL, NAT)"

# Commit 2
git commit -m "feat: implement diagnosis pipeline (Rule Checker -> Keyword Filter -> LLM)"

# Commit 3
git commit -m "feat: add LLM client with fallback chain (Gemma 4 -> auto)"

# Commit 4
git commit -m "feat: add prompt library with system prompt + 3 worked examples"

# Commit 5
git commit -m "test: add diagnosis & evaluator tests (10 tests passing)"

# Push
git push origin part2-pipeline
```

---

## Part 3: Human Review, Dashboard & Evaluation
**Responsible AI** - Review workflow + HTML Dashboard + Evaluation

### Files to Add
```
backend/
├── src/
│   ├── human_review.py         # Accepted/Edited/Rejected workflow + Markdown log
│   ├── dashboard.py            # HTML + Chart.js dashboard generator
│   └── evaluator.py            # Batch evaluation with accuracy metrics
├── data/
│   ├── human_review_log.md     # Append-only review log
│   └── dashboard.html          # Generated HTML dashboard
├── docs/
│   ├── INDEX.md                # Documentation hub
│   ├── ARCHITECTURE.md         # System design
│   ├── API_REFERENCE.md        # Complete API docs
│   ├── VSCODE_SETUP.md         # IDE configuration
│   ├── TESTING.md              # Testing guide
│   └── TROUBLESHOOTING.md      # Common issues
└── main_cli.py                 # Updated with review, dashboard, rule-check commands
```

### Commands
```bash
# Create branch from part2
git checkout part2-pipeline
git checkout -b part3-review-dashboard

# Add files
git add backend/src/human_review.py backend/src/dashboard.py backend/src/evaluator.py
git add backend/data/human_review_log.md backend/main_cli.py
git add backend/docs/INDEX.md backend/docs/ARCHITECTURE.md backend/docs/API_REFERENCE.md
git add backend/docs/VSCODE_SETUP.md backend/docs/TESTING.md backend/docs/TROUBLESHOOTING.md

# Commit 1
git commit -m "feat: add human review workflow (Accepted/Edited/Rejected + Markdown log)"

# Commit 2
git commit -m "feat: add HTML dashboard with Chart.js (stats, charts, tables, review log)"

# Commit 3
git commit -m "feat: add evaluation system (batch accuracy, per-case results)"

# Commit 4
git commit -m "docs: add complete documentation (Architecture, API, Testing, VS Code, Troubleshooting)"

# Commit 5
git commit -m "feat: update CLI with review log, dashboard generation, rule check commands"

# Push
git push origin part3-review-dashboard
```

---

## Part 4: FastAPI Server + Frontend Web UI
**Web Interface** - FastAPI server + 5 pages + 15 REST endpoints + WebSocket

### Files to Add
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
├── .vscode/                    # VS Code configs
└── GITHUB_PUSH_STRATEGY.md
```

### Commands
```bash
# Create branch from part3
git checkout part3-review-dashboard
git checkout -b part4-web-api

# Add files
git add backend/main.py
git add frontend/
git add .vscode/
git add GITHUB_PUSH_STRATEGY.md

# Commit 1
git commit -m "feat: add FastAPI server with lifespan, static files, Jinja2 templates"

# Commit 2
git commit -m "feat: implement 5 web pages (Home, Dashboard, Diagnose, Cases, Review)"

# Commit 3
git commit -m "feat: add 15 REST API endpoints (diagnose, rule-check, review, dashboard, evaluate)"

# Commit 4
git commit -m "feat: add WebSocket support for real-time diagnosis updates"

# Commit 5
git commit -m "feat: add responsive CSS + vanilla JS (API calls, toasts, modals, charts)"

# Commit 6
git commit -m "feat: add Chart.js integration (doughnut + bar charts) to dashboard"

# Commit 7
git commit -m "feat: add VS Code configs (settings, launch, tasks, snippets)"

# Commit 8
git commit -m "fix: TemplateResponse signature for Starlette/FastAPI compatibility"

# Push
git push origin part4-web-api
```

---

## Final: Merge All Parts to Main

```bash
# Create main branch from part4
git checkout part4-web-api
git checkout -b main

# Push main
git push origin main

# Tag release
git tag -a v1.0.0 -m "v1.0.0: NetSage AI - Complete with CLI, Web UI, API, Dashboard, Human Review"
git push origin v1.0.0

# Clean up feature branches (optional)
git branch -d part1-foundation part2-pipeline part3-review-dashboard part4-web-api
git push origin --delete part1-foundation part2-pipeline part3-review-dashboard part4-web-api
```

---

## Commit Message Format

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

## Pre-Push Checklist (Each Part)

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