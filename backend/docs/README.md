# NetSage AI - Cisco Network Troubleshooting Assistant

> **An AI-assisted troubleshooter for Cisco Packet Tracer lab problems that reads symptoms and show-command output, suggests likely causes and next steps, and requires human review before accepting any fix.**

## Overview

NetSage AI is a responsible AI system designed to help junior network engineers connect symptoms to root causes in Cisco-style lab networks. The assistant analyzes structured troubleshooting evidence (symptoms, Packet Tracer notes, show-command outputs) and recommends:

- **Likely fault** (from 30 known categories)
- **OSI layer** and **concept tag**
- **Confidence score** (0.0-1.0)
- **Evidence-backed reasoning**
- **Next commands to run**
- **Step-by-step fix with Cisco CLI commands**

**Safety Rule:** Every AI diagnosis must be reviewed by a human before acceptance. The system enforces an **Accepted / Edited / Rejected** workflow with full audit logging.

---

## Features

| Feature | Description |
|---------|-------------|
| **30 Fault Categories** | VLAN, gateway, DHCP, DNS, routing, ACL, NAT, wireless |
| **Deterministic Rule Checker** | 10 Python checks for common config errors (runs before AI) |
| **AI Diagnosis Pipeline** | Keyword filtering  Structured prompt  LLM  JSON output |
| **Human Review Workflow** | Accepted / Edited / Rejected with reasoning capture |
| **Responsible AI Log** | Markdown log of all reviews (5+ corrected cases required) |
| **HTML Dashboard** | Issue types, severity, AI agreement rate, case tables |
| **Prompt Library** | `diagnose_prompt.md` with system prompt + 3 worked examples |
| **Evaluation System** | Accuracy, per-case results, confusion tracking |
| **CLI Interface** | 8 commands for full lifecycle management |

---

## Architecture

```

  Packet Tracer    (External simulator - not automated)

          CLI Evidence (show outputs, ping, ipconfig)
         

 data/evidence/    case_XX.txt (structured sections)

         
         

           DIAGNOSIS PIPELINE               
  1. Rule Checker (deterministic, 10 rules) 
  2. Keyword Filter  Candidate Cases       
  3. Prompt Builder + Worked Examples       
  4. OpenRouter LLM (free models w/ fallback)
  5. JSON Parser  DiagnosisResult          

         
         
     
 Human Review           Evaluation     
 Accept/Edit/           Accuracy       
 Reject + Log           Per-case table 
     
                                
                                
     
 Review Log .md        Dashboard .html 
     
```

---

## 30 Fault Categories

| ID | Fault | Concept | Severity | OSI Layer |
|----|-------|---------|----------|-----------|
| 1 | Wrong IP Address | IP Addressing | Medium | Layer 3 |
| 2 | Wrong Subnet Mask | Subnet Mask | Medium | Layer 3 |
| 3 | Wrong Default Gateway | Default Gateway | Medium | Layer 3 |
| 4 | Interface Shutdown | Interface Status | High | Layer 1/2 |
| 5 | Missing VLAN | VLAN | High | Layer 2 |
| 6 | Wrong Access VLAN | VLAN | Medium | Layer 2 |
| 7 | Trunk Configuration Problem | VLAN Trunking | High | Layer 2 |
| 8 | VLAN Allowed List Mismatch | VLAN Trunking | High | Layer 2 |
| 9 | Missing Inter-VLAN Subinterface | Inter-VLAN Routing | High | Layer 3 |
| 10 | Missing Subinterface | Inter-VLAN Routing | High | Layer 3 |
| 11 | Wrong VLAN Encapsulation | Inter-VLAN / 802.1Q | High | Layer 2/3 |
| 12 | DHCP Pool Missing | DHCP | High | Layer 3 |
| 13 | Wrong DHCP Network | DHCP | High | Layer 3 |
| 14 | Wrong DHCP Gateway | DHCP / Default Gateway | High | Layer 3 |
| 15 | DHCP Addresses Exhausted | DHCP Pool Exhaustion | Medium | Layer 3 |
| 16 | Missing Route | Routing | High | Layer 3 |
| 17 | Wrong Static Route | Static Routing | High | Layer 3 |
| 18 | Router Interface Down | Router Interface | High | Layer 1/3 |
| 19 | Wrong Network Address | IP Addressing / Routing | High | Layer 3 |
| 20 | Wrong DNS Server | DNS | Medium | Layer 3/7 |
| 21 | Missing DNS Record | DNS | Medium | Layer 7 |
| 22 | DNS Server Unreachable | DNS Connectivity | High | Layer 3/7 |
| 23 | ACL Blocks Traffic | ACL | High | Layer 3/4 |
| 24 | ACL on Wrong Interface | ACL | High | Layer 3/4 |
| 25 | Wrong ACL Order | ACL | High | Layer 3/4 |
| 26 | NAT Missing | NAT | High | Layer 3 |
| 27 | NAT Inside/Outside Mistake | NAT | High | Layer 3 |
| 28 | NAT ACL Mismatch | NAT / ACL | High | Layer 3 |
| 29 | Wireless Configuration Problem | Wireless Networking | Medium | Layer 2 |
| 30 | Wireless  Internal Server Problem | Wireless / Internal Server | High | Layer 3 |

---

## Installation

### Prerequisites
- Python 3.11+
- OpenRouter API key (free tier at https://openrouter.ai)

### Setup

```bash
# Clone / navigate to project
cd Cisco_project

# Create virtual environment
python -m venv .venv

# Activate
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Dependencies
```
pandas>=2.0.0
pydantic>=2.0.0
python-dotenv>=1.0.0
openai>=1.0.0          # For OpenRouter API
google-genai>=2.18.0   # Optional: Google AI Studio fallback
pytest>=7.0.0          # For tests
```

---

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

```env
# OpenRouter (primary)
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxx
OPENROUTER_MODEL=openrouter/auto   # or specific free model

# Google AI Studio (fallback - optional)
GOOGLE_API_KEY=AQ.xxxxxxxxxxxx
GOOGLE_MODEL=gemini-2.5-flash
```

**Model Notes:**
- `openrouter/auto` routes to best available free model
- Free models have rate limits; fallback chain handles this automatically
- For production, use a paid model (e.g., `openai/gpt-4o-mini`)

---

## Quick Start

```bash
# 1. Validate dataset
python main.py
# Choose option 3

# 2. Run a diagnosis (case 1 has evidence)
python main.py
# Choose option 2
# Enter case ID: 1
# Paste evidence (or press Enter to use file)

# 3. Review the AI output
# Choose: Accepted / Edited / Rejected

# 4. View dashboard
python main.py
# Choose option 6

# 5. Run evaluation
python main.py
# Choose option 4
```

---

## CLI Reference

| Command | Description |
|---------|-------------|
| `1` List Cases | Show all 30 faults with concept & severity |
| `2` Diagnose Case | Run rule checker  AI diagnosis  human review prompt |
| `3` Validate Dataset | CSV integrity (30 cases, required columns, no duplicates) |
| `4` Evaluate Model | Batch evaluation with accuracy report |
| `5` Human Review Log | Show Accepted/Edited/Rejected stats + corrected cases |
| `6` Generate Dashboard | Create & open `data/dashboard.html` in browser |
| `7` Rule Checker | Run deterministic checks on specific case |
| `8` Exit | Quit |

---

## Evidence Format

Create `data/evidence/case_XX.txt` with structured sections:

```text
[user_description]
PC1 cannot reach PC2. Both on same switch. PC1 has wrong IP subnet.

[ping_results]
Pinging 192.168.1.20 with 32 bytes of data:
Request timed out. (4 times)
Packets: Sent = 4, Received = 0, Lost = 4 (100% loss)

[ipconfig]
IPv4 Address: 192.168.2.10
Subnet Mask: 255.255.255.0
Default Gateway: 0.0.0.0

[show_ip_interface_brief]
GigabitEthernet0/0 192.168.1.1 up up
GigabitEthernet0/1 192.168.2.1 up up

[show_running_config]
interface FastEthernet0/1
 switchport mode access
 switchport access vlan 10

[show_vlan_brief]
VLAN Name                             Status    Ports
1    default                          active    Fa0/1, Fa0/2
10   STAFF                            active    Fa0/1
20   STUDENTS                         active    Fa0/2

[show_interfaces_trunk]
Port        Mode         Encapsulation  Status        Native vlan
Fa0/24      on           802.1q         trunking      1

[show_ip_route]
Gateway of last resort is not set
     192.168.1.0/24 is directly connected, GigabitEthernet0/0

[show_access_lists]
Standard IP access list 1
    10 permit 192.168.1.0 0.0.0.255

[show_ip_nat_translations]
Pro  Inside global      Inside local       Outside local      Outside global
---  203.0.113.1        192.168.1.10       ---                ---

[other_cli_output]
Any additional relevant output
```

**Generate templates:**
```bash
python -c "from src.evidence_parser import create_all_placeholders; create_all_placeholders()"
```

---

## Rule Checker (Deterministic)

Runs **before** AI diagnosis. Catches common config errors without LLM.

| Check | Detects |
|-------|---------|
| `wrong_subnet_mask` | Mask 255.255.0.0, 255.0.0.0 on /24 networks |
| `gateway_mismatch` | Default gateway not in same subnet as IP |
| `interface_down` | "administratively down" in show output |
| `missing_vlan` | VLAN referenced but absent from `show vlan brief` |
| `missing_route` | Destination not in `show ip route` |
| `dhcp_pool_missing` | No `ip dhcp pool` or client has 169.254.x.x |
| `dhcp_wrong_network` | Pool network  interface network |
| `dhcp_wrong_gateway` | Pool `default-router`  actual gateway |
| `acl_blocking` | Deny rule matching expected traffic |
| `nat_missing` | No `ip nat inside/outside` or translations empty |

**Run standalone:**
```bash
python main.py
# Option 7  Enter case ID
```

---

## Human Review Workflow

After each diagnosis, the CLI prompts:

```
Log human review? (y/n): y

Options:
  1. Accepted - AI diagnosis is correct
  2. Edited - AI partially correct, needs correction
  3. Rejected - AI diagnosis is wrong

Decision (1/2/3): 2

Notes: AI confused Case 11 with Case 10

--- Provide Corrections ---
Corrected Fault: Wrong VLAN Encapsulation
Corrected Confidence (0-1): 0.95
Corrected Reasoning: Subinterface G0/0.20 has dot1Q 30 not 20
Corrected Fix: Change encapsulation to dot1Q 20
Corrected Commands: enable, conf t, int g0/0.20, encap dot1Q 20
```

**Log entry written to:** `data/human_review_log.md`

**Review Log contains:**
- Case ID, title, timestamp
- AI output (fault, confidence, reasoning, fix, commands)
- Human decision (Accepted/Edited/Rejected)
- Corrections (if Edited/Rejected)
- Human notes

---

## Responsible AI Log

The project requires **5 cases where AI was corrected** (Edited or Rejected).

**View corrected cases:**
```bash
python main.py
# Option 5
```

Output:
```
Total Reviews: 12
  Accepted:  8
  Edited:    3
  Rejected:  1
AI Agreement Rate: 66.7%

Corrected Cases:
  Case 11: Wrong VLAN Encapsulation - Edited
    AI: Missing Subinterface
    Human: Wrong VLAN Encapsulation
  Case 15: DHCP Addresses Exhausted - Rejected
    AI: DHCP Pool Missing
    Human: DHCP Addresses Exhausted
```

---

## Dashboard

**Generate:** Option 6 in CLI or:
```bash
python -c "from src.dashboard import generate_dashboard; generate_dashboard()"
```

**Opens:** `data/dashboard.html` in browser

**Contains:**
- **Stats Cards:** Total cases, Accepted/Edited/Rejected, AI agreement rate
- **Issue Types:** Bar chart by concept (VLAN, DHCP, Routing, etc.)
- **Severity Distribution:** High/Medium/Low with progress bars
- **Review Log Table:** All Edited/Rejected cases with AI vs Human
- **All 30 Cases Table:** ID, Fault, Concept, Severity, OSI Layer

---

## Prompt Library

**File:** `diagnose_prompt.md`

Contains:
1. **System Prompt** - Rules 1-12 (no guessing, cite evidence, JSON only)
2. **Output Schema** - JSON with 7 required fields
3. **3 Worked Examples** - Wrong DHCP Gateway, Missing VLAN, Trunk Problem
4. **All 30 Categories Table** - Reference for prompt injection
5. **Key Distinctions** - How to differentiate similar cases (DHCP 12-15, Inter-VLAN 9-11, ACL 23-25, NAT 26-28)

**Prompt Construction:**
```
[System Prompt]
+
[User Evidence - structured sections]
+
[Filtered Candidate Cases - title, expected_fault, concept, severity]
=
Final Prompt  LLM
```

---

## Evaluation

```bash
python main.py
# Option 4
```

**Output:**
```
MODEL EVALUATION REPORT
============================================================
Total Evaluated: 15
Correct Predictions: 14
Accuracy: 93.33%

Case | Expected                                    | Predicted                                | Correct
--------------------------------------------------------------------------------
   1 | Wrong IP Address                            | Wrong IP Address                         | 
   2 | Wrong Subnet Mask                           | Wrong Subnet Mask                        | 
  ...
  11 | Wrong VLAN Encapsulation                    | Missing Subinterface                     | 
  ...
```

**Requirements:**
- Compares `predicted_fault` vs `expected_fault` (case-insensitive partial match)
- Only evaluates cases with evidence files
- Reports per-case correctness

---

## Project Structure

```
network-troubleshooting-ai/
 data/
    cases.csv                    # 30 cases (SOURCE OF TRUTH - never modify)
    evidence/
       case_01.txt ... case_30.txt  # Evidence files (15 populated)
       (create with create_all_placeholders())
    dashboard.html               # Generated HTML dashboard
    human_review_log.md          # Append-only review log
 src/
    __init__.py
    config.py                    # .env loading, paths, constants
    models.py                    # Pydantic: Case, Evidence, DiagnosisResult
    data_loader.py               # CSV load, validate, query
    evidence_parser.py           # Parse evidence files, create templates
    rule_checker.py              # 10 deterministic checks
    diagnosis.py                 # Pipeline: Rules  Filter  LLM  Result
    llm_client.py                # OpenRouter + fallback models
    prompts.py                   # System prompt, prompt builders
    human_review.py              # Accepted/Edited/Rejected workflow
    dashboard.py                 # HTML dashboard generator
    evaluator.py                 # Accuracy evaluation
    utils.py                     # CLI helpers, logging
 tests/
    test_data_loader.py          # 5 tests
    test_diagnosis.py            # 5 tests
    test_evaluator.py            # 5 tests
 diagnose_prompt.md               # Prompt library with examples
 main.py                          # CLI entry point (8 commands)
 requirements.txt
 .env.example
 .gitignore
 README.md
```

---

## Adding New Cases

1. **Add row to `data/cases.csv`** (keep IDs sequential 1-30+)
2. **Validate:** `python main.py`  Option 3
3. **Create evidence:** `data/evidence/case_XX.txt` with structured sections
4. **Test:** `python main.py`  Option 2  Enter case ID

---

## Keyword Filtering

Edit `CONCEPT_KEYWORDS` in `src/diagnosis.py`:

```python
CONCEPT_KEYWORDS = {
    "DHCP": ["dhcp", "ip dhcp pool", "default-router", "169.254", "dhcp pool"],
    "VLAN": ["vlan", "access vlan", "switchport access"],
    # Add more keywords to improve candidate selection
}
```

---

## Testing

```bash
# Run all tests
$env:PYTHONPATH="."; pytest tests/ -v

# Expected: 15 passed
# test_data_loader: load, get_case, by_concept, by_title, validate
# test_diagnosis: filter_dhcp, filter_vlan, empty_evidence, normalize, validation
# test_evaluator: exact_match, case_insensitive, partial, no_match, substring
```

---

## Limitations & Safety

| Limitation | Mitigation |
|------------|------------|
| Packet Tracer not automated | Evidence manually collected |
| AI depends on evidence quality | Rule checker runs first; `needs_more_evidence` flag |
| LLM can hallucinate | Human review required; worked examples in prompt |
| Free models rate-limited | Fallback chain (3+ models) |
| Not for production networks | Educational/simulation use only |

---

## Responsible AI Compliance

| Requirement | Implementation |
|-------------|----------------|
| Human review every case | CLI prompts after each diagnosis |
| Accepted/Edited/Rejected | 3-way decision captured |
| 5+ corrected cases | Log shows Edited + Rejected count |
| Audit trail | `human_review_log.md` (append-only) |
| Transparency | Dashboard shows AI agreement rate |

---

## License

Educational project for Cisco networking + AI integration learning. Not for production use.

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: src` | Run with `$env:PYTHONPATH="."` or `python -m` |
| OpenRouter 401/404/429 | Check `.env` API key; try different free model |
| Google AI 404 | Use `gemini-2.5-flash` or update model list |
| Dashboard won't open | Check `data/dashboard.html` exists; open manually |
| Evidence not loaded | Verify `data/evidence/case_XX.txt` exists and has content |
| Rule checker false positives | Refine regex in `src/rule_checker.py` |

---

## Contributing

1. Add evidence for cases 16-30
2. Improve rule checker coverage
3. Add more worked examples to `diagnose_prompt.md`
4. Extend dashboard with trend charts
5. Add support for more LLM providers

---

**Built for:** Applied AI + Network Troubleshooting (NetSage AI)  
**Team Size:** 2-3 students  
**Safety Rule:** Human review required for every diagnosis