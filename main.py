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

# Ensure the project root is on sys.path when running as `python main.py`.
sys.path.insert(0, str(Path(__file__).parent))

from tui.app import EXIT_CODE_RESTART


def main() -> None:
    # Deferred imports so the restart exec path stays fast.
    from agent import build_crew
    from tui.app import LocalAgentApp

    print("Initialising agent (loading model and memory)…", flush=True)
    crew = build_crew()
    app = LocalAgentApp(crew)
    app.run()

    if app.return_code == EXIT_CODE_RESTART:
        print("Restarting…", flush=True)
        os.execv(sys.executable, [sys.executable] + sys.argv)


if __name__ == "__main__":
    main()
