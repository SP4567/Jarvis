import os
import json
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Load .env file from project root or server directory
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

class Settings:
    PROJECT_NAME: str = "JARVIS Live Engine"
    VERSION: str = "2.0.0"
    
    # Host & Port
    HOST: str = os.getenv("JARVIS_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("JARVIS_PORT", "8000"))
    
    # Security & Authentication
    API_KEY: str = os.getenv("JARVIS_API_KEY", "jarvis-dev-secret-key-2026")
    REQUIRE_AUTH: bool = os.getenv("JARVIS_REQUIRE_AUTH", "false").lower() == "true"
    CORS_ORIGINS: List[str] = [
        origin.strip() for origin in os.getenv(
            "JARVIS_CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000"
        ).split(",") if origin.strip()
    ]
    
    # Gemini API Key & Models
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    LIVE_MODEL: str = os.getenv("JARVIS_LIVE_MODEL", "gemini-3.1-flash-live-preview")
    TEXT_MODEL: str = os.getenv("JARVIS_TEXT_MODEL", "gemini-2.5-flash")
    
    # TTS Settings
    TTS_VOICE: str = os.getenv("JARVIS_TTS_VOICE", "en-GB-RyanNeural")  # Sophisticated British / JARVIS accent
    TTS_RATE: str = os.getenv("JARVIS_TTS_RATE", "+5%")
    TTS_PITCH: str = os.getenv("JARVIS_TTS_PITCH", "+0Hz")
    
    # Database / Memory (Unified Async Storage)
    DATA_DIR: Path = Path(__file__).resolve().parent / "data"
    DB_PATH: Path = DATA_DIR / "jarvis_memory.db"
    SOC_DB_PATH: Path = DATA_DIR / "soc_cases.db"
    ENABLE_WAL_MODE: bool = True
    
    # Guardrails Config
    GUARDRAIL_STRICTNESS: str = os.getenv("GUARDRAIL_STRICTNESS", "strict")  # relaxed | normal | strict
    AUTO_APPROVE_TIER2: bool = os.getenv("AUTO_APPROVE_TIER2", "true").lower() == "true"
    DUAL_APPROVAL_REQUIRED_TIER3: bool = os.getenv("DUAL_APPROVAL_REQUIRED_TIER3", "true").lower() == "true"
    APPROVAL_TIMEOUT_SECONDS: int = int(os.getenv("APPROVAL_TIMEOUT_SECONDS", "90"))
    
    # Threat Intelligence Feeds
    ABUSEIPDB_API_KEY: str = os.getenv("ABUSEIPDB_API_KEY", "")
    OTX_API_KEY: str = os.getenv("OTX_API_KEY", "")
    VIRUSTOTAL_API_KEY: str = os.getenv("VIRUSTOTAL_API_KEY", "")
    CTI_CACHE_TTL_HOURS: int = int(os.getenv("CTI_CACHE_TTL_HOURS", "24"))
    
    # System Execution Workspace
    WORKSPACE_ROOT: Path = Path(__file__).resolve().parent.parent

settings = Settings()
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
