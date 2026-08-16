# Troubleshooting Guide

## Common Issues

### 1. Module Import Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError: src` | PYTHONPATH not set | `$env:PYTHONPATH="."; python main.py` |
| `ModuleNotFoundError: fastapi` | Deps not installed | `pip install -r requirements.txt` |
| `ModuleNotFoundError: google.generativeai` | Optional dep missing | `pip install google-genai` |

**Quick Fix:**
```bash
cd backend
.venv\Scripts\Activate.ps1
$env:PYTHONPATH="."
pip install -r requirements.txt
```

---

### 2. OpenRouter API Issues

| Error | Cause | Solution |
|-------|-------|----------|
| `401 Unauthorized` | Invalid/missing API key | Check `.env` has valid `OPENROUTER_API_KEY` |
| `404 Model not found` | Model unavailable | Use `openrouter/auto` or check model list |
| `429 Rate Limited` | Free tier exhausted | Wait, or use fallback chain (auto-handled) |
| `500 Internal Server Error` | Provider error | Retry, fallback triggers automatically |

**Debug:**
```bash
# Check API key
cat .env | grep OPENROUTER_API_KEY

# Test API directly
curl -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  https://openrouter.ai/api/v1/models
```

---

### 3. Template Rendering Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `TypeError: cannot use 'tuple' as a dict key` | Jinja2 cache issue | Restart server, or clear `__pycache__` |
| `TemplateSyntaxError: unexpected char '?'` | JS ternary in template | Replace `a ? b : c` with `b if a else c` |
| `UndefinedError: 'list object' has no attribute 'length'` | Wrong filter | Use `corrected|length` not `corrected.length` |

**Fix Template Cache:**
```bash
# Clear cache
rm -rf backend/__pycache__ backend/src/__pycache__ backend/tests/__pycache__
```

---

### 4. Evidence Not Loading

| Symptom | Cause | Solution |
|---------|-------|----------|
| "No evidence found" | File missing | Check `data/evidence/case_XX.txt` exists |
| Empty evidence | Wrong format | Ensure sections use `[section_name]` format |
| Wrong case loaded | ID mismatch | Check case_id matches filename |

**Generate Missing Evidence Files:**
```bash
python -c "from src.evidence_parser import create_all_placeholders; create_all_placeholders()"
```

---

### 5. Rate Limiting / LLM Issues

| Issue | Workaround |
|-------|------------|
| Gemma 4 rate limited | Fallback to `openrouter/auto` |
| All models rate limited | Wait 5-10 min, or add paid credits |
| JSON parsing fails | Check prompt formatting, fallback handles most |

**Check Model Status:**
```bash
curl -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  https://openrouter.ai/api/v1/models | jq '.data[] | select(.id | contains("free")) | .id'
```

---

### 5. Dashboard Not Opening

| Issue | Solution |
|-------|----------|
| File not found | Run `python main_cli.py` → Option 6 |
| Browser blocks | Allow popups for localhost |
| Charts not rendering | Check Chart.js CDN in template |

**Manual Open:**
```bash
# Windows
start backend\data\dashboard.html

# Linux/macOS
xdg-open backend/data/dashboard.html
```

---

### 6. Human Review Log Issues

| Issue | Solution |
|-------|----------|
| Log not updating | Check write permissions on `data/human_review_log.md` |
| Stats show 0 | Run a diagnosis → choose review option |
| Markdown not rendering | Open in VS Code / GitHub / Markdown viewer |

---

### 7. Database/CSV Issues

| Error | Solution |
|-------|----------|
| "Duplicate IDs" | Check `cases.csv` for duplicate case_id |
| "Missing columns" | Compare with expected schema |
| "Case IDs 1-30 missing" | Ensure all 30 cases present |

**Validate:**
```bash
python -c "from src.data_loader import validate_dataset, print_validation_report; print_validation_report(validate_dataset())"
```

---

### 8. Virtual Environment Issues

| Problem | Fix |
|-------|-----|
| "Command not found" | Re-activate: `.venv\Scripts\Activate.ps1` |
| Wrong Python version | Recreate: `python -m venv .venv --python=3.11` |
| Packages not found | `pip install -r requirements.txt --force-reinstall` |

---

### 9. Port Already in Use

```bash
# Find process on port 8000
netstat -ano | findstr :8000

# Kill process (replace PID)
taskkill /PID <PID> /F

# Or use different port
python -c "import uvicorn; uvicorn.run('main:app', host='127.0.0.1', port=8001)"
```

---

### 10. Windows-Specific Issues

| Issue | Fix |
|-------|-----|
| `Activate.ps1` not allowed | `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| Path too long | Enable long paths: `git config --system core.longpaths true` |
| PowerShell errors | Run as Administrator |

---

## Debug Commands

```bash
# Check server health
curl http://127.0.0.1:8000/api/health

# Test diagnosis
curl -X POST http://127.0.0.1:8000/api/diagnose \
  -H "Content-Type: application/json" \
  -d '{"case_id": 1, "evidence_text": "[ipconfig]\nIP: 192.168.2.10\nMask: 255.255.255.0\nGateway: 0.0.0.0"}'

# Check logs
Get-Content backend\app.log -Wait

# View review log
cat backend\data\human_review_log.md
```

---

## Getting Help

1. Check this guide first
2. Check `backend/app.log` for errors
3. Run with debug: `python -c "import logging; logging.basicConfig(level=logging.DEBUG); import main"`
4. Search existing issues
5. Create new issue with:
   - Error message
   - Steps to reproduce
   - Environment (OS, Python version)
   - Relevant log snippets