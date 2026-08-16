# Architecture Documentation

## System Overview

NetSage AI is a **responsible AI system** for Cisco network troubleshooting that combines:
- **Deterministic rule checking** (fast, reliable)
- **LLM-based diagnosis** (flexible, contextual)
- **Human-in-the-loop** (safety, accountability)

---

## Data Flow

```
┌──────────────────┐
│  Packet Tracer   │  (External simulator)
│   Lab Setup      │
└────────┬─────────┘
         │ Manual collection
         ▼
┌──────────────────┐
│  Evidence Files  │  data/evidence/case_XX.txt
│  (Structured)    │  [user_description], [ipconfig], etc.
└────────┬─────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│                    DIAGNOSIS PIPELINE                        │
├─────────────────────────────────────────────────────────────┤
│  1. RULE CHECKER (Deterministic)                            │
│     ├─ 10 checks: subnet, gateway, interface, VLAN, etc.   │
│     └─ Output: issues[] or pass                             │
│                                                             │
│  2. KEYWORD FILTER                                          │
│     ├─ Map evidence → concepts (30 categories)             │
│     └─ Output: candidate_cases[]                            │
│                                                             │
│  3. PROMPT BUILDER                                          │
│     ├─ System prompt + worked examples                      │
│     ├─ User evidence + candidate cases                      │
│     └─ Output: structured prompt                            │
│                                                             │
│  4. LLM CLIENT (OpenRouter)                                 │
│     ├─ Primary: google/gemma-4-26b-a4b-it:free             │
│     ├─ Fallback: openrouter/auto                            │
│     ├─ Response format: JSON (enforced)                     │
│     └─ Output: DiagnosisResult                              │
│                                                             │
│  4. HUMAN REVIEW                                            │
│     ├─ Accepted / Edited / Rejected                         │
│     └─ Logged to Markdown                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## Core Modules

### 1. Data Layer (`src/data_loader.py`)
- **load_cases()** - Load 30 cases from CSV
- **validate_dataset()** - Integrity checks
- **get_case(id)** - Single case lookup
- **get_cases_by_concept()** - Filter by concept

### 2. Evidence Parser (`src/evidence_parser.py`)
- **parse_evidence_file()** - Parse structured sections
- **load_evidence(case_id)** - Load from file
- **create_all_placeholders()** - Generate templates

### 3. Rule Checker (`src/rule_checker.py`)
10 deterministic checks (runs BEFORE LLM):
| Check | Detects |
|-------|---------|
| `wrong_subnet_mask` | 255.255.0.0 on /24 |
| `gateway_mismatch` | Gateway not in subnet |
| `interface_down` | "administratively down" |
| `missing_vlan` | VLAN missing from show vlan |
| `missing_route` | Route absent from table |
| `dhcp_pool_missing` | No pool or 169.254.x.x |
| `dhcp_wrong_network` | Pool network ≠ interface |
| `dhcp_wrong_gateway` | Pool default-router wrong |
| `acl_blocking` | Deny matches traffic |
| `nat_missing` | No ip nat inside/outside |

### 4. Diagnosis Pipeline (`src/diagnosis.py`)
```python
def diagnose(evidence, case_id=None):
    # 1. Rule checker (deterministic)
    rule_results = run_rule_checker(evidence, case)
    
    # 2. Keyword filter → candidate cases
    candidates = filter_candidate_cases(evidence, all_cases)
    
    # 3. Build prompt + LLM
    prompt = build_diagnosis_prompt(evidence, candidates)
    response = llm_client.diagnose(SYSTEM_PROMPT, prompt)
    
    # 4. Return structured result
    return DiagnosisResult(...)
```

### 5. LLM Client (`src/llm_client.py`)
- **Fallback chain**: Primary → Fallback 1 → Fallback 2
- **Response parsing**: Robust JSON extraction
- **Models**: gemma-4-26b-it:free → openrouter/auto → others

### 6. Human Review (`src/human_review.py`)
- **Accepted** - AI correct
- **Edited** - AI partially correct (capture corrections)
- **Rejected** - AI wrong (capture correct diagnosis)
- **Log format**: Markdown (`human_review_log.md`)

### 7. Dashboard (`src/dashboard.py`)
- **HTML output**: Bootstrap 5 + Chart.js
- **Charts**: Doughnut (concepts), Bar (severity)
- **Tables**: All cases, corrected cases, review log

### 8. Evaluator (`src/evaluator.py`)
- Batch evaluation of all cases with evidence
- **Metrics**: Accuracy, per-case correctness
- **Comparison**: Case-insensitive partial match

---

## Data Models

### Case
```python
class Case(BaseModel):
    case_id: int
    title: str
    topology: str
    symptom: str
    topology_note: str
    show_outputs: str
    expected_fault: str
    osi_layer: str
    concept: str
    severity: Severity  # Low | Medium | High
```

### Evidence
```python
class Evidence(BaseModel):
    case_id: Optional[int]
    user_description: str
    ping_results: str
    ipconfig: str
    show_ip_interface_brief: str
    show_running_config: str
    show_vlan_brief: str
    show_interfaces_trunk: str
    show_ip_route: str
    show_access_lists: str
    show_ip_nat_translations: str
    other_cli_output: str
```

### DiagnosisResult
```python
class DiagnosisResult(BaseModel):
    case_id: int
    predicted_fault: str
    confidence: float  # 0.0-1.0
    reasoning_summary: str
    evidence_used: List[str]
    recommended_fix: str
    commands: List[str]
    needs_more_evidence: bool
```

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Rule checker first | Catches obvious errors instantly, reduces LLM calls |
| Keyword filtering | Reduces prompt size, improves accuracy |
| JSON-only LLM output | Enforced via `response_format={"type": "json_object"}` |
| Fallback models | Free tier rate limits require fallback chain |
| Human review required | Safety rule - no auto-apply to production |
| Markdown log | Human-readable, version-controllable |
| HTML dashboard | Zero-dependency, browser-based |

---

## Security Considerations

| Aspect | Implementation |
|--------|----------------|
| API Keys | Environment variables only (`.env`) |
| Input Validation | Pydantic models on all endpoints |
| Rate Limiting | Fallback chain handles 429 |
| CORS | Not configured (local dev only) |
| WebSocket | Echo-only, no auth (local dev) |

---

## Scalability Notes

| Component | Current | Scaling Path |
|-----------|---------|--------------|
| Cases | 30 | CSV → Database |
| Evidence | Files | Object storage |
| LLM Calls | Sequential | Async batch |
| Dashboard | Static HTML | React/Vue SPA |
| Review Log | Markdown | Database |

---

## Deployment Notes

### Development
```bash
python main.py  # http://localhost:8000
```

### Production Considerations
- Add authentication (OAuth/JWT)
- Configure CORS
- Add rate limiting middleware
- Use PostgreSQL for cases/evidence/reviews
- Add Redis for caching
- Configure reverse proxy (nginx)
- Enable HTTPS
- Add monitoring (Prometheus/Grafana)