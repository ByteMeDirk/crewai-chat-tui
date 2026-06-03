"""
log.py - Application-wide logging configuration.

Writes structured log records to agent.log in the project root.
Import and use the module-level `logger` anywhere in the codebase:

    from log import logger
    logger.info("Something happened")
    logger.error("Something broke", exc_info=True)

Log file location: <project_root>/agent.log
Log level:        DEBUG (all levels captured in the file)
Format:           2026-06-03 12:00:00,123 [LEVEL   ] module:line - message
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

_LOG_PATH = Path(__file__).parent / "agent.log"

_FMT = "%(asctime)s [%(levelname)-8s] %(name)s:%(lineno)d - %(message)s"
_DATE_FMT = "%Y-%m-%d %H:%M:%S"


def _setup() -> logging.Logger:
    root = logging.getLogger()
    if root.handlers:
        # Already configured (e.g. re-import after restart exec)
        return logging.getLogger("agent")

    root.setLevel(logging.DEBUG)

    # Rotating file handler — keep last 2 × 1 MB slices so the log never
    # grows unbounded, but you still have enough history to diagnose issues.
    try:
        from logging.handlers import RotatingFileHandler
        fh = RotatingFileHandler(
            _LOG_PATH,
            maxBytes=1 * 1024 * 1024,  # 1 MB
            backupCount=2,
            encoding="utf-8",
        )
    except OSError as e:
        # Fallback: log to stderr if we can't open the file (e.g. read-only FS)
        print(f"[log.py] Cannot open log file {_LOG_PATH}: {e}", file=sys.stderr)
        fh = logging.StreamHandler(sys.stderr)  # type: ignore[assignment]

    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(_FMT, datefmt=_DATE_FMT))
    root.addHandler(fh)

    # Silence noisy third-party loggers that would otherwise flood the file.
    for noisy in (
        "httpx",
        "httpcore",
        "urllib3",
        "asyncio",
        "lancedb",
        "lance",
        "opentelemetry",
        "crewai.telemetry",
    ):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    return logging.getLogger("agent")


logger = _setup()
