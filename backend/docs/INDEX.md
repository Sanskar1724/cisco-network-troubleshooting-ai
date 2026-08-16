# NetSage AI - Documentation Hub

## Overview
Complete documentation for the NetSage AI - Cisco Network Troubleshooting Assistant.

---

## Quick Links

| Document | Description |
|----------|-------------|
| [Project README](../README.md) | Quick start & overview |
| [Full Documentation](FULL_DOCS.md) | Complete project documentation |
| [Prompt Library](diagnose_prompt.md) | System prompt + 3 worked examples |
| [API Reference](API_REFERENCE.md) | Complete API documentation |
| [Architecture](ARCHITECTURE.md) | System design & data flow |
| [VS Code Setup](VSCODE_SETUP.md) | IDE configuration |
| [Testing Guide](TESTING.md) | How to run tests |
| [Troubleshooting](TROUBLESHOOTING.md) | Common issues & fixes |

---

## Quick Start

```bash
cd backend

# 1. Setup
python -m venv .venv && .venv\Scripts\activate && pip install -r requirements.txt

# 2. Configure
cp .env.example .env  # Add OPENROUTER_API_KEY

# 3. CLI
python main_cli.py

# 4. Web Server
python main.py  # http://localhost:8000

# 5. Tests
$env:PYTHONPATH="."; pytest tests/ -v
```

---

## Architecture Overview

```
┌─────────────┐    Evidence     ┌──────────────┐
│Packet Tracer│ ──────────────► │data/evidence/│
└─────────────┘   (manual)      └──────┬───────┘
                                       │
                                       ▼
┌─────────────┐    Diagnosis      ┌──────────────┐
│  Frontend   │ ◄──────────────── │   Backend    │
│ (Templates) │   JSON + WS       │  (FastAPI)   │
└─────────────┘                   └──────┬───────┘
                                        │
                    ┌───────────────────┼───────────────────┐
                    ▼                   ▼                   ▼
              ┌───────────┐      ┌─────────────┐     ┌─────────────┐
              │Rule Check │      │Keyword Filter│    │   LLM       │
              │(10 checks)│      │(30 concepts) │     │(OpenRouter) │
              └───────────┘      └─────────────┘     └─────────────┘
                    │                   │                   │
                    └───────────────────┼───────────────────┘
                                        ▼
                              ┌─────────────────┐
                              │DiagnosisResult  │
                              │(JSON: fault,    │
                              │ confidence,     │
                              │ fix, commands)  │
                              └────────┬────────┘
                                       │
                                       ▼
                              ┌─────────────────┐
                              │Human Review     │
                              │Accept/Edit/Reject│
                              └────────┬────────┘
                                       │
                                       ▼
                              ┌─────────────────┐
                              │Dashboard + Log  │
                              │(HTML + Markdown)│
                              └─────────────────┘
```

---

## 30 Fault Categories

| ID | Fault | Concept | Severity |
|----|-------|---------|----------|
| 1 | Wrong IP Address | IP Addressing | Medium |
| 2 | Wrong Subnet Mask | Subnet Mask | Medium |
| 3 | Wrong Default Gateway | Default Gateway | Medium |
| 4 | Interface Shutdown | Interface Status | High |
| 5 | Missing VLAN | VLAN | High |
| 6 | Wrong Access VLAN | VLAN | Medium |
| 7 | Trunk Configuration Problem | VLAN Trunking | High |
| 8 | VLAN Allowed List Mismatch | VLAN Trunking | High |
| 9 | Missing Inter-VLAN Subinterface | Inter-VLAN Routing | High |
| 10 | Missing Subinterface | Inter-VLAN Routing | High |
| 11 | Wrong VLAN Encapsulation | Inter-VLAN / 802.1Q | High |
| 12 | DHCP Pool Missing | DHCP | High |
| 13 | Wrong DHCP Network | DHCP | High |
| 14 | Wrong DHCP Gateway | DHCP / Default Gateway | High |
| 15 | DHCP Addresses Exhausted | DHCP Pool Exhaustion | Medium |
| 16 | Missing Route | Routing | High |
| 17 | Wrong Static Route | Static Routing | High |
| 18 | Router Interface Down | Router Interface | High |
| 19 | Wrong Network Address | IP Addressing / Routing | High |
| 20 | Wrong DNS Server | DNS | Medium |
| 21 | Missing DNS Record | DNS | Medium |
| 22 | DNS Server Unreachable | DNS Connectivity | High |
| 23 | ACL Blocks Traffic | ACL | High |
| 24 | ACL on Wrong Interface | ACL | High |
| 25 | Wrong ACL Order | ACL | High |
| 26 | NAT Missing | NAT | High |
| 27 | NAT Inside/Outside Mistake | NAT | High |
| 28 | NAT ACL Mismatch | NAT / ACL | High |
| 29 | Wireless Configuration Problem | Wireless Networking | Medium |
| 30 | Wireless → Internal Server Problem | Wireless / Internal Server | High |

---

## Key Commands

| Task | Command |
|------|---------|
| Start CLI | `python main_cli.py` |
| Start Web Server | `python main.py` |
| Run Tests | `$env:PYTHONPATH="."; pytest tests/ -v` |
| Validate Data | `python main_cli.py` → Option 3 |
| Run Evaluation | `python main_cli.py` → Option 4 |
| Generate Dashboard | `python main_cli.py` → Option 6 |
| View Review Log | `python main_cli.py` → Option 5 |

---

## Key Files Reference

| File | Purpose |
|------|---------|
| `src/rule_checker.py` | 10 deterministic checks |
| `src/diagnosis.py` | Pipeline: Rules → Filter → LLM |
| `src/llm_client.py` | OpenRouter + fallback models |
| `src/human_review.py` | Accepted/Edited/Rejected workflow |
| `src/dashboard.py` | HTML + Chart.js generator |
| `src/diagnosis.py` | Pipeline orchestration |
| `src/data_loader.py` | CSV load & validation |
| `diagnose_prompt.md` | System prompt + examples |
| `frontend/templates/*.html` | 5 web pages |

---

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENROUTER_API_KEY` | API key for OpenRouter | Required |
| `OPENROUTER_MODEL` | Model to use | `openrouter/auto` |
| `GOOGLE_API_KEY` | Google AI Studio key | Optional |
| `GOOGLE_MODEL` | Google model | `gemini-2.5-flash` |

---

## Testing

```bash
cd backend
$env:PYTHONPATH="."; pytest tests/ -v
# 15 tests: data_loader(5), diagnosis(5), evaluator(5)
```

---

## Project Structure

```
backend/
├── main.py              # FastAPI server
├── main_cli.py          # CLI (8 commands)
├── requirements.txt
├── .env / .env.example
├── data/
│   ├── cases.csv        # 30 cases (source of truth)
│   ├── evidence/        # 30 evidence files
│   ├── dashboard.html   # Generated HTML
│   └── human_review_log.md
├── docs/                # All documentation
├── scripts/             # Utility scripts
├── src/ (10 modules)
│   ├── config.py
│   ├── models.py
│   ├── data_loader.py
│   ├── evidence_parser.py
│   ├── rule_checker.py
│   ├── diagnosis.py
│   ├── llm_client.py
│   ├── prompts.py
│   ├── human_review.py
│   ├── dashboard.py
│   ├── evaluator.py
│   └── utils.py
├── tests/ (15 tests)
frontend/
├── static/css, js, data/
└── templates/ (5 pages)
```

---

## Resources

- [OpenRouter](https://openrouter.ai) - Free LLM API
- [Google AI Studio](https://aistudio.google.com) - Free Gemini API
- [Chart.js](https://www.chartjs.org) - Dashboard charts
- [FastAPI](https://fastapi.tiangolo.com) - Backend framework
- [Jinja2](https://jinja.palletsprojects.com) - Templates

---

## License

Educational project for Cisco networking + AI integration learning. Not for production use.