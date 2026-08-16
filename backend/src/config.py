"""Configuration management for the Cisco Network Troubleshooting AI."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CASES_CSV = DATA_DIR / "cases.csv"
EVIDENCE_DIR = DATA_DIR / "evidence"

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/auto")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

LLM_TIMEOUT = 60
LLM_TEMPERATURE = 0.1
LLM_MAX_TOKENS = 2000