"""
API Management Utility for NanoP

Provides tools to manage and validate API keys (Gemini, OpenAI, etc.).
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv, set_key

# Default model if not configured in .env
DEFAULT_GEMINI_MODEL = "gemini-2.0-flash"


def load_api_keys():
    """Load API keys from .env file."""
    env_path = Path(".env")
    if env_path.exists():
        load_dotenv(env_path)
        return True
    return False


def get_default_model() -> str:
    """
    Get the default Gemini model from environment variable.
    
    Configure in .env file:
        GEMINI_MODEL=gemini-2.0-flash
    
    Returns:
        Model name string (defaults to gemini-2.0-flash if not set)
    """
    load_api_keys()  # Ensure .env is loaded
    return os.environ.get("GEMINI_MODEL", DEFAULT_GEMINI_MODEL)

def set_gemini_key(api_key: str):
    """Save Gemini API key to .env file."""
    env_path = Path(".env")
    if not env_path.exists():
        env_path.touch()
    
    set_key(str(env_path), "GOOGLE_API_KEY", api_key)
    # Refresh local environment
    os.environ["GOOGLE_API_KEY"] = api_key
    return True

def validate_gemini_key(api_key: str = None):
    """
    Validate Gemini API key by making a simple metadata call.
    Returns (bool, message).
    """
    key = api_key or os.environ.get("GOOGLE_API_KEY")
    if not key:
        return False, "No Gemini API key found in environment."

    try:
        import google.generativeai as genai
        genai.configure(api_key=key)
        # Try to list models (simple light-weight call)
        models = genai.list_models()
        # If we can iterate even one model, the key is valid
        next(iter(models))
        return True, "Successfully validated Gemini API key."
    except Exception as e:
        return False, f"Validation failed: {str(e)}"

def get_masked_key(key_name: str = "GOOGLE_API_KEY"):
    """Get a masked version of the key for display."""
    key = os.environ.get(key_name)
    if not key:
        return "Not Set"
    if len(key) <= 8:
        return "****"
    return f"{key[:4]}...{key[-4:]}"
