"""Configuration settings for the Banking Swarm Demo.

Supports Meta Developer Model API (Muse: muse-spark, muse-wonder)
via OpenAI-compatible completions interface, ChromaDB persistence,
and graceful simulation fallback when credentials are not configured.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

# Meta Developer Model API (Muse)
# Meta Model API is drop-in compatible with Chat Completions API
META_API_KEY = os.getenv("META_API_KEY") or os.getenv("MODEL_API_KEY") or os.getenv("OPENAI_API_KEY")
META_API_BASE = os.getenv("META_API_BASE", "https://api.meta.ai/v1")
META_MODEL = os.getenv("META_MODEL", "muse-spark")

# Force or default simulation mode
_sim_env = os.getenv("SIMULATION_MODE", "").lower()
if _sim_env in ("1", "true", "yes"):
    SIMULATION_MODE = True
elif _sim_env in ("0", "false", "no"):
    SIMULATION_MODE = False
else:
    # Auto-enable simulation if no API key is provided
    SIMULATION_MODE = bool(not META_API_KEY or META_API_KEY.startswith("your_"))

# ChromaDB Settings
CHROMA_PERSIST_DIR = str(BASE_DIR / "chroma_db")
DOCUMENTS_DIR = str(BASE_DIR / "rag" / "documents")

