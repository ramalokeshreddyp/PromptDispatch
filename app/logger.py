"""
Logging utility — appends each route decision to route_log.jsonl
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

LOG_FILE = os.getenv("LOG_FILE", "route_log.jsonl")


def log_route(intent: str, confidence: float, user_message: str, final_response: str) -> None:
    """Append a single JSON line to the log file."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "intent": intent,
        "confidence": confidence,
        "user_message": user_message,
        "final_response": final_response,
    }
    log_path = Path(LOG_FILE)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
