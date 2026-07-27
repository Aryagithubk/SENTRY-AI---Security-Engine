import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
MOCK_DATA_DIR = BASE_DIR / "mock_data"

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mock").lower()
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Mock Data Paths
ALERTS_FILE = MOCK_DATA_DIR / "alerts.json"
USERS_FILE = MOCK_DATA_DIR / "users.json"
ENDPOINTS_FILE = MOCK_DATA_DIR / "endpoints.json"
INCIDENTS_FILE = MOCK_DATA_DIR / "incidents.json"
LOGIN_HISTORY_FILE = MOCK_DATA_DIR / "login_history.json"
THREAT_INTEL_FILE = MOCK_DATA_DIR / "threat_intelligence.json"
