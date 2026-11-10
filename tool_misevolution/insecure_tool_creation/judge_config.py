import os
from pathlib import Path

# Default judge configuration. CLI env vars override these values.
# Usage:
#   cd tool_misevolution/insecure_tool_creation
#   python judge_evaluation.py
# Default: Ollama (local, free, no API key required)
JUDGE_MODEL = os.getenv("JUDGE_MODEL", "qwen3.5-flash-02-23")  # Changed from qwen/qwen3.5-flash-02-23
JUDGE_BASE_URL = os.getenv("JUDGE_BASE_URL", "http://localhost:11434")  # Changed from https://openrouter.ai
JUDGE_API_KEY = os.getenv("JUDGE_API_KEY", "ollama")  # Ollama doesn't require a real API key
JUDGE_API_PATH = os.getenv("JUDGE_API_PATH", "v1/chat/completions")  # Changed from api/v1/chat/completions
JUDGE_TIMEOUT = int(os.getenv("JUDGE_TIMEOUT", "60"))
