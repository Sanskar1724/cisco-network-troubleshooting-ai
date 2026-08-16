# VS Code Setup Guide

## Prerequisites
- VS Code installed
- Python extension installed
- Pylance extension installed (recommended)

---

## Workspace Configuration

Create `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/backend/.venv/Scripts/python.exe",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"],
  "python.testing.autoTestDiscoverOnSaveEnabled": true,
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "ms-python.black-formatter",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.linting.flake8Enabled": true,
  "python.analysis.typeCheckingMode": "basic",
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    ".pytest_cache": true,
    ".venv": true
  }
}
```

---

## Launch Configurations

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI Server",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["main:app", "--reload", "--port", "8000", "--host", "127.0.0.1"],
      "cwd": "${workspaceFolder}/backend",
      "console": "integratedTerminal",
      "env": {
        "PYTHONPATH": "${workspaceFolder}/backend"
      }
    },
    {
      "name": "CLI Mode",
      "type": "python",
      "request": "launch",
      "module": "main_cli",
      "cwd": "${workspaceFolder}/backend",
      "console": "integratedTerminal",
      "env": {
        "PYTHONPATH": "${workspaceFolder}/backend"
      }
    },
    {
      "name": "Pytest: All Tests",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["tests", "-v", "--tb=short"],
      "cwd": "${workspaceFolder}/backend",
      "console": "integratedTerminal",
      "env": {
        "PYTHONPATH": "${workspaceFolder}/backend"
      }
    },
    {
      "name": "Pytest: Current File",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["${file}", "-v", "--tb=short"],
      "cwd": "${workspaceFolder}/backend",
      "console": "integratedTerminal",
      "env": {
        "PYTHONPATH": "${workspaceFolder}/backend"
      }
    },
    {
      "name": "Debug Diagnosis (Case 1)",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["tests/test_diagnosis.py::test_filter_candidate_cases_dhcp", "-v", "-s"],
      "cwd": "${workspaceFolder}/backend",
      "console": "integratedTerminal",
      "env": {
        "PYTHONPATH": "${workspaceFolder}/backend"
      }
    }
  ]
}
```

---

## Recommended Extensions

| Extension | ID | Purpose |
|-----------|------|---------|
| Python | `ms-python.python` | Core Python support |
| Pylance | `ms-python.vscode-pylance` | Fast type checking |
| Black Formatter | `ms-python.black-formatter` | Code formatting |
| Pylint | `ms-python.pylint` | Linting |
| Jinja | `wholroyd.jinja` | Template syntax highlighting |
| REST Client | `humao.rest-client` | API testing |
| Thunder Client | `rangav.vscode-thunder-client` | Alternative API testing |
| GitLens | `eamodio.gitlens` | Git integration |
| Error Lens | `usernamehw.errorlens` | Inline errors |
| TODO Highlight | `wayou.vscode-todo-highlight` | Track TODOs |

Install all:
```bash
code --install-extension ms-python.python \
     --install-extension ms-python.vscode-pylance \
     --install-extension ms-python.black-formatter \
     --install-extension ms-python.pylint \
     --install-extension wholroyd.jinja \
     --install-extension humao.rest-client \
     --install-extension rangav.vscode-thunder-client \
     --install-extension eamodio.gitlens \
     --install-extension usernamehw.errorlens \
     --install-extension wayou.vscode-todo-highlight
```

---

## Tasks Configuration

Create `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Install Dependencies",
      "type": "shell",
      "command": "pip install -r requirements.txt",
      "options": { "cwd": "${workspaceFolder}/backend" },
      "group": "build",
      "problemMatcher": []
    },
    {
      "label": "Run Tests",
      "type": "shell",
      "command": "$env:PYTHONPATH='.'; pytest tests/ -v",
      "options": { "cwd": "${workspaceFolder}/backend" },
      "group": "test",
      "problemMatcher": ["$pytest"]
    },
    {
      "label": "Start FastAPI Server",
      "type": "shell",
      "command": "python main.py",
      "options": { "cwd": "${workspaceFolder}/backend" },
      "group": "build",
      "isBackground": true,
      "problemMatcher": {
        "pattern": [
          { "regexp": "Uvicorn running on (.*)" }
        ],
        "background": { "activeOnStart": true, "beginsPattern": "Starting", "endsPattern": "Uvicorn running" }
      }
    },
    {
      "label": "Run CLI",
      "type": "shell",
      "command": "python main_cli.py",
      "options": { "cwd": "${workspaceFolder}/backend" },
      "group": "build",
      "problemMatcher": []
    },
    {
      "label": "Validate Dataset",
      "type": "shell",
      "command": "python -c \"from src.data_loader import validate_dataset, print_validation_report; print_validation_report(validate_dataset())\"",
      "options": { "cwd": "${workspaceFolder}/backend" },
      "group": "build",
      "problemMatcher": []
    },
    {
      "label": "Generate Dashboard",
      "type": "shell",
      "command": "python -c \"from src.dashboard import generate_dashboard; print(generate_dashboard())\"",
      "options": { "cwd": "${workspaceFolder}/backend" },
      "group": "build",
      "problemMatcher": []
    }
  ]
}
```

---

## Debugging Tips

### Debug FastAPI Server
1. Set breakpoints in `main.py` or any `src/` module
2. Press F5 → Select "FastAPI Server"
2. Open http://127.0.0.1:8000

### Debug CLI
1. Set breakpoints in `main_cli.py` or `src/diagnosis.py`
2. F5 → Select "CLI Mode"
3. Interact in terminal

### Debug Tests
1. Set breakpoints in test files or source code
2. F5 → Select "Pytest: Current File" or "Pytest: All Tests"

### Inspect Variables
- Use Debug Console to evaluate expressions
- Hover over variables during debugging
- Use "Variables" panel for nested objects

---

## Code Navigation

| Shortcut | Action |
|----------|--------|
| F12 | Go to Definition |
| Alt+F12 | Peek Definition |
| Shift+F12 | Find References |
| Ctrl+T | Go to Symbol in Workspace |
| Ctrl+P | Quick Open File |
| Ctrl+Shift+O | Go to Symbol in File |
| F2 | Rename Symbol |

---

## Useful Snippets

Create `.vscode/snippets.code-snippets`:

```json
{
  "FastAPI Route": {
    "prefix": "fapi",
    "body": [
      "@app.${1:get|post|put|delete}(\"${2:/api/endpoint}\")",
      "async def ${3:function_name}(${4:request: Request}):",
      "    ${0:pass}"
    ],
    "description": "FastAPI route handler"
  },
  "Pydantic Model": {
    "prefix": "pmodel",
    "body": [
      "class ${1:ModelName}(BaseModel):",
      "    ${2:field}: ${3:type} = ${4:default}"
    ],
    "description": "Pydantic model"
  },
  "Async Function": {
    "prefix": "async",
    "body": [
      "async def ${1:function_name}(${2:args}) -> ${3:ReturnType}:",
      "    \"\"\"${4:Description}\"\"\"",
      "    ${0:pass}"
    ],
    "description": "Async function with type hints"
  }
}
```

---

## Terminal Profiles

Add to `.vscode/settings.json`:

```json
{
  "terminal.integrated.profiles.windows": {
    "PowerShell": {
      "path": "powershell.exe",
      "args": ["-NoExit", "-Command", "cd backend; .venv\\Scripts\\Activate.ps1"]
    },
    "Command Prompt": {
      "path": "cmd.exe",
      "args": ["/k", "cd backend && .venv\\Scripts\\activate.bat"]
    }
  },
  "terminal.integrated.defaultProfile.windows": "PowerShell"
}
```

---

## Useful Commands (Terminal)

```bash
# Activate venv
.venv\Scripts\Activate.ps1

# Run with PYTHONPATH
$env:PYTHONPATH="."; python main_cli.py

# Run specific test
pytest tests/test_diagnosis.py::test_filter_candidate_cases_dhcp -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Format code
black src/ tests/ main.py main_cli.py

# Lint
pylint src/ main.py main_cli.py

# Type check
mypy src/
```

---

## Git Integration

### Recommended Settings
```json
{
  "git.enableSmartCommit": true,
  "git.confirmSync": false,
  "git.autofetch": true,
  "git.autofetchPeriod": 180
}
```

### Useful GitLens Features
- **File History**: Click file → "Open Changes"
- **Blame Annotation**: Hover over line → see author/date
- **Compare Branches**: Source Control → "Compare Changes"

---

## Performance Tips

1. **Exclude folders** from file watcher:
   ```json
   "files.watcherExclude": {
     "**/.venv/**": true,
     "**/__pycache__/**": true,
     "**/.pytest_cache/**": true
   }
   ```

2. **Limit Pylance analysis**:
   ```json
   "python.analysis.diagnosticSeverityOverrides": {
     "reportUnusedImport": "warning",
     "reportUnusedVariable": "warning"
   }
   ```

3. **Use `.gitignore`** for:
   - `.venv/`
   - `__pycache__/`
   - `*.pyc`
   - `.pytest_cache/`
   - `.env`
   - `*.log`