import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

LOGS_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

AUDIT_LOG_FILE = LOGS_DIR / "audit.log"
AUDIT_JSON_FILE = LOGS_DIR / "audit_records.json"

# Configure standard audit logger
audit_logger = logging.getLogger("SecureOps-Audit")
audit_logger.setLevel(logging.INFO)

if not audit_logger.handlers:
    fh = logging.FileHandler(AUDIT_LOG_FILE, encoding="utf-8")
    fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    audit_logger.addHandler(fh)

class AuditService:
    """Enterprise Audit Logging Service for compliance, accountability, and security tracking."""

    @staticmethod
    def _load_audit_records() -> List[Dict[str, Any]]:
        if not AUDIT_JSON_FILE.exists():
            return []
        try:
            with open(AUDIT_JSON_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    @staticmethod
    def _save_audit_records(records: List[Dict[str, Any]]):
        with open(AUDIT_JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2)

    @classmethod
    def log_event(
        cls,
        user_id: str,
        user_role: str,
        action: str,
        resource: str = "N/A",
        investigation_id: Optional[str] = "N/A",
        session_id: Optional[str] = "SESSION-DEFAULT",
        result: str = "SUCCESS",
        details: Optional[str] = ""
    ) -> Dict[str, Any]:
        """
        Record a compliance audit event.
        """
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        event = {
            "timestamp": now_str,
            "user_id": user_id,
            "user_role": user_role,
            "action": action,
            "resource": resource,
            "investigation_id": investigation_id or "N/A",
            "session_id": session_id or "SESSION-DEFAULT",
            "result": result,
            "details": details or ""
        }

        # Log line formatted string to file
        log_line = f"USER={user_id} | ROLE={user_role} | ACTION={action} | RESOURCE={resource} | RESULT={result} | DETAILS={details}"
        audit_logger.info(log_line)

        # Store JSON record
        records = cls._load_audit_records()
        records.insert(0, event)  # newest first
        # Keep last 500 records
        if len(records) > 500:
            records = records[:500]
        cls._save_audit_records(records)

        return event

    @classmethod
    def get_audit_logs(cls, limit: int = 100) -> List[Dict[str, Any]]:
        return cls._load_audit_records()[:limit]
