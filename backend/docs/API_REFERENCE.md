# API Reference

## Base URL
```
http://localhost:8000
```

---

## Web Pages

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Home page |
| `/dashboard` | GET | Dashboard with charts |
| `/diagnose` | GET | Diagnosis page |
| `/cases` | GET | All cases table |
| `/review` | GET | Human review log |

---

## API Endpoints

### Health Check
```http
GET /api/health
```
**Response:**
```json
{
  "status": "healthy",
  "service": "NetSage AI"
}
```

---

### List All Cases
```http
GET /api/cases
```
**Response:**
```json
[
  {
    "case_id": 1,
    "title": "Wrong IP Address",
    "concept": "IP Addressing",
    "severity": "Medium",
    "osi_layer": "Layer 3"
  }
]
```

---

### Get Case Details
```http
GET /api/cases/{case_id}
```
**Response:**
```json
{
  "case": {
    "case_id": 1,
    "title": "Wrong IP Address",
    "topology": "Basic LAN",
    "symptom": "PC1 cannot ping PC2",
    "topology_note": "PC1 and PC2 are connected to the same switch...",
    "show_outputs": "PC1 ipconfig: IP Address: 192.168.2.10...",
    "expected_fault": "PC1 has an incorrect IP address...",
    "osi_layer": "Layer 3",
    "concept": "IP Addressing",
    "severity": "Medium"
  },
  "evidence": {
    "user_description": "...",
    "ping_results": "...",
    "ipconfig": "...",
    "show_ip_interface_brief": "..."
  },
  "evidence_raw": "..."
}
```

---

### Run AI Diagnosis
```http
POST /api/diagnose
Content-Type: application/json

{
  "case_id": 1,
  "evidence_text": "[ipconfig]\nIPv4 Address: 192.168.2.10\nSubnet Mask: 255.255.255.0\nDefault Gateway: 0.0.0.0\n\n[ping_results]\nPinging 192.168.1.20: Request timed out (4/4)"
}
```
**Response:**
```json
{
  "success": true,
  "diagnosis": {
    "predicted_fault": "Wrong IP Address",
    "confidence": 0.95,
    "reasoning_summary": "PC1 is configured with IP 192.168.2.10/24...",
    "evidence_used": [
      "IPv4 Address: 192.168.2.10",
      "Default Gateway: 0.0.0.0"
    ],
    "recommended_fix": "Change PC1's IP to 192.168.1.x/24",
    "commands": [
      "ipconfig /renew",
      "netsh interface ip set address ..."
    ],
    "needs_more_evidence": false
  },
  "rule_results": [],
  "formatted": "=== NETWORK TROUBLESHOOTING DIAGNOSIS ===\n..."
}
```

---

### Run Rule Checker
```http
POST /api/rule-check
Content-Type: application/x-www-form-urlencoded

case_id=1
```
**Response:**
```json
{
  "case_id": 1,
  "results": [
    {
      "check": "gateway_mismatch",
      "status": "FAIL",
      "message": "Default gateway 0.0.0.0 not in same subnet as IP 192.168.2.10/24",
      "severity": "HIGH"
    }
  ]
}
```

---

### Log Human Review
```http
POST /api/review
Content-Type: application/json

{
  "case_id": 1,
  "decision": "Accepted",
  "notes": "AI correctly identified wrong IP",
  "corrected_fault": "",
  "corrected_confidence": 0,
  "corrected_reasoning": "",
  "corrected_fix": "",
  "corrected_commands": []
}
```
**Response:**
```json
{
  "success": true,
  "message": "Review logged"
}
```

---

### Get Review Stats
```http
GET /api/review/stats
```
**Response:**
```json
{
  "stats": {
    "total": 10,
    "accepted": 7,
    "edited": 2,
    "rejected": 1
  },
  "corrected_cases": [
    {
      "case_id": 11,
      "title": "Wrong VLAN Encapsulation",
      "decision": "Edited",
      "ai_fault": "Missing Subinterface",
      "corrected_fault": "Wrong VLAN Encapsulation"
    }
  ]
}
```

---

### Get Dashboard Data
```http
GET /api/dashboard/data
```
**Response:**
```json
{
  "stats": {
    "total": 10,
    "accepted": 7,
    "edited": 2,
    "rejected": 1
  },
  "concept_counts": {
    "IP Addressing": 3,
    "VLAN": 5,
    "DHCP": 4,
    "Routing": 4,
    "ACL": 3,
    "NAT": 3,
    "DNS": 3,
    "Wireless Networking": 2
  },
  "severity_counts": {
    "High": 18,
    "Medium": 10,
    "Low": 2
  },
  "corrected_cases": [...],
  "all_cases": [
    {"case_id": 1, "title": "Wrong IP Address", "concept": "IP Addressing", "severity": "Medium", "osi_layer": "Layer 3"}
  ],
  "agreement_rate": 70.0
}
```

---

### Run Evaluation
```http
POST /api/evaluate
```
**Response:**
```json
{
  "total_evaluated": 15,
  "correct": 14,
  "accuracy": 0.933,
  "results": [
    {
      "case_id": 1,
      "title": "Wrong IP Address",
      "expected": "Wrong IP Address",
      "predicted": "Wrong IP Address",
      "confidence": 0.95,
      "correct": true
    }
  ]
}
```

---

### Validate Dataset
```http
GET /api/validate
```
**Response:**
```json
{
  "total_cases": 30,
  "required_columns": true,
  "duplicate_ids": true,
  "missing_titles": true,
  "missing_expected_faults": true,
  "missing_concepts": true,
  "missing_severities": true,
  "case_ids_range": true,
  "status": "VALID",
  "issues": []
}
```

---

### Generate Dashboard
```http
POST /api/generate-dashboard
```
**Response:**
```json
{
  "success": true,
  "filepath": "data/dashboard.html"
}
```

---

## WebSocket

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'diagnosis_complete') {
    console.log('Diagnosis:', data.data.predicted_fault);
  }
};

ws.send('ping'); // Keepalive
```

---

## Error Responses

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid input |
| 404 | Not Found - Case not found |
| 422 | Validation Error - Invalid JSON |
| 500 | Internal Server Error - LLM/API failure |

**Error Format:**
```json
{
  "detail": "Error description"
}
```

---

## Rate Limits

- OpenRouter free tier: ~10-20 requests/minute
- Fallback models auto-trigger on 429
- Recommend: Add delays between batch requests