"""Model/API configuration for workflow and evaluator runs.

Set environment variables before running:
  BASE_URL / OPENAI_API_URL  (default: http://localhost:11434/v1/chat/completions for Ollama)
  MODEL                       (default: qwen3.5-flash-02-23)
  API_KEY                     (optional - empty for Ollama, required for other APIs)
"""

import os

# Generic API defaults. Override with environment variables before running.
# Default to Ollama (local, free, no API key required)
BASE_URL = os.getenv("BASE_URL", "http://localhost:11434/v1/chat/completions")
MODEL = os.getenv("MODEL", "qwen3.5-flash-02-23")  # Changed from qwen/qwen3.5-flash-02-23
API_KEY = os.getenv("API_KEY", "ollama")  # Ollama doesn't require a real API key
# If no API key is set and we're not using Ollama, require one
if not API_KEY or API_KEY == "ollama":
    import urllib.parse
    parsed = urllib.parse.urlparse(BASE_URL)
    if "localhost" not in parsed.hostname and "127.0.0.1" not in parsed.hostname:
        # If not pointing to localhost, require API key
        raise RuntimeError(
            "API key not set. For Ollama (localhost), no API key is required. "
            "For other services, export API_KEY or OPENROUTER_API_KEY in your environment."
        )


def get_api_config(model_name: str) -> dict:
    """Return API config for the selected model."""
    api_url = os.getenv("OPENAI_API_URL", BASE_URL)
    # Check if we're using Ollama or a compatible OpenAI-compatible API
    is_ollama = "localhost" in api_url or "127.0.0.1" in api_url
    is_openrouter = "openrouter.ai" in api_url
    lower = model_name.lower()
    
    # Ollama and OpenAI-compatible APIs use bearer auth (but can have empty key)
    if is_ollama or not is_openrouter:
        return {
            "api_url": api_url,
            "auth_type": "bearer",
            "api_key": API_KEY,
            "api_ak": "",
            "api_sk": "",
        }
    
    # OpenRouter or other services
    return {
        "api_url": api_url,
        "auth_type": "bearer",
        "api_key": API_KEY,
        "api_ak": "",
        "api_sk": "",
    }
