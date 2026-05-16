"""
core/logger.py
Logging system terpusat untuk Teleoder.

Tanggung jawab:
- Log event internal (info, warning, error)
- Tulis ke file log harian (logs/YYYY-MM-DD.log)
- Append mode, tidak overwrite
- Thread-safe via lock
"""

import os
import threading
from datetime import datetime


# ─── Constants ────────────────────────────────────────────────────────────────

LOG_DIR = "logs"

LEVEL_INFO  = "INFO "
LEVEL_WARN  = "WARN "
LEVEL_ERROR = "ERROR"

_lock = threading.Lock()


# ─── Internal Helpers ─────────────────────────────────────────────────────────

def _get_log_path() -> str:
    """Return path file log hari ini."""
    today = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(LOG_DIR, f"{today}.log")


def _write(level: str, message: str):
    """
    Tulis satu baris log ke file.
    Thread-safe via lock.
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    line = f"[{timestamp}] {level} {message}\n"

    with _lock:
        os.makedirs(LOG_DIR, exist_ok=True)
        with open(_get_log_path(), "a", encoding="utf-8") as f:
            f.write(line)


# ─── Public API ───────────────────────────────────────────────────────────────

def log_info(message: str):
    """Log event informasi normal."""
    _write(LEVEL_INFO, message)


def log_warn(message: str):
    """Log warning — sesuatu tidak ideal tapi masih jalan."""
    _write(LEVEL_WARN, message)


def log_error(message: str):
    """Log error — sesuatu gagal."""
    _write(LEVEL_ERROR, message)
