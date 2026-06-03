"""
main.py - Entry point for the Local Agent TUI.

Usage:
    python main.py              # local terminal
    ttyd -p 7681 python main.py # LAN access via browser at http://<host>:7681

Restart behaviour:
    The TUI exits with EXIT_CODE_RESTART (3) when the user requests a restart
    (Ctrl+R or the Restart button in the quit dialog). main() detects this and
    re-executes the current process via os.execv, which replaces the process
    in-place - clean slate, same PID group, works correctly under ttyd.
"""
import os
import sys
from pathlib import Path

# Disable crewai's OTLP telemetry before any crewai import.
# Without this, BatchSpanProcessor tries to connect to telemetry.crewai.com:4319
# at startup and blocks for up to 30 s when the host is unreachable.
os.environ.setdefault("CREWAI_DISABLE_TELEMETRY", "true")
os.environ.setdefault("OTEL_SDK_DISABLED", "true")

# Ensure the project root is on sys.path when running as `python main.py`.
sys.path.insert(0, str(Path(__file__).parent))

from log import logger
from tui.app import EXIT_CODE_RESTART


def _shutdown_memory(agent: "Agent") -> None:  # type: ignore[name-defined]  # noqa: F821
    """Drain pending memory saves and shut down the background thread pool.

    Memory._save_pool is a ThreadPoolExecutor. If we exit while a save is
    in-flight Python's atexit waits indefinitely for the thread to finish,
    causing a hung shutdown. Calling drain_writes() + shutdown(wait=False)
    avoids the hang.
    """
    try:
        memory = getattr(agent, "memory", None)
        if memory is None:
            return
        drain = getattr(memory, "drain_writes", None)
        if drain:
            drain()
        pool = getattr(memory, "_save_pool", None)
        if pool:
            pool.shutdown(wait=False, cancel_futures=True)
    except Exception:
        pass


def main() -> None:
    # Deferred imports so the restart exec path stays fast.
    from agent import build_agent
    from tui.app import LocalAgentApp

    logger.info("=" * 60)
    logger.info("Starting crewai-chat-tui")
    print("Initialising agent (loading model and memory)…", flush=True)
    try:
        agent = build_agent()
        logger.info("Agent built successfully")
    except Exception:
        logger.critical("Failed to build agent", exc_info=True)
        raise

    app = LocalAgentApp(agent)
    try:
        app.run()
    except Exception:
        logger.critical("Unhandled exception in TUI", exc_info=True)
        raise
    finally:
        logger.info("TUI exited (return_code=%s)", getattr(app, "return_code", "?"))
        _shutdown_memory(agent)

    if app.return_code == EXIT_CODE_RESTART:
        logger.info("Restarting process")
        print("Restarting…", flush=True)
        os.execv(sys.executable, [sys.executable] + sys.argv)


if __name__ == "__main__":
    main()
