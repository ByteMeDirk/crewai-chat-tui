"""
Textual TUI for the local conversational agent.

Key bindings:
  Enter       - send message
  Ctrl+C      - quit (with confirmation)
  Ctrl+R      - restart (reloads agent and clears memory)
  Ctrl+L      - clear chat history
  Escape      - cancel current request (if thinking)

Exit codes used by main.py:
  0 - normal quit
  3 - restart requested (main.py will re-exec the process)
"""
from __future__ import annotations

import asyncio
import sys
from datetime import datetime
from pathlib import Path
from typing import ClassVar

from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    RichLog,
)

from log import logger
from tui.utils.css import APP_CSS
from tui.utils.dialogs import ConfirmScreen
from tui.utils.widgets import StatusBar

# Exit code that main.py watches for to trigger a restart.
EXIT_CODE_RESTART = 3

# Add parent to path so imports work whether launched via `python tui/app.py`
# or via `python main.py`.
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import CFG


class LocalAgentApp(App):
    """Main Textual application."""

    TITLE = CFG["tui"]["title"]
    CSS = APP_CSS
    BINDINGS: ClassVar[list[Binding]] = [
        Binding("ctrl+c", "confirm_exit", "Quit/Restart", show=True),
        Binding("ctrl+r", "restart", "Restart", show=True),
        Binding("ctrl+l", "clear_chat", "Clear", show=True),
        Binding("escape", "cancel_request", "Cancel", show=False),
    ]

    _thinking: bool = False
    _cancel_event: asyncio.Event | None = None

    def __init__(self, agent):
        super().__init__()
        self._agent = agent
        self._history: list[dict] = []  # running conversation history

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="chat-container"):
            yield RichLog(id="chat-log", highlight=True, markup=True, wrap=True)
        with Horizontal(id="input-row"):
            yield Input(placeholder="Type a message…", id="user-input")
            yield Button("Send", id="send-btn", variant="primary")
        yield StatusBar(id="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        self._log_system("Agent ready. Type a message and press Enter.")
        self.query_one("#user-input", Input).focus()

    def _log(self, text: str, css_class: str = "msg-agent") -> None:
        """Append a line to the chat log with optional markup class."""
        log = self.query_one("#chat-log", RichLog)
        ts = datetime.now().strftime("%H:%M")
        log.write(f"[dim]{ts}[/dim]  [{css_class}]{text}[/{css_class}]")

    def _log_user(self, text: str) -> None:
        self._log(f"You: {text}", "msg-user")

    def _log_agent(self, text: str) -> None:
        self._log(f"Agent: {text}", "msg-agent")

    def _log_error(self, text: str) -> None:
        self._log(f"Error: {text}", "msg-error")

    def _log_system(self, text: str) -> None:
        self._log(text, "msg-system")

    def _set_input_enabled(self, enabled: bool) -> None:
        self.query_one("#user-input", Input).disabled = not enabled
        self.query_one("#send-btn", Button).disabled = not enabled

    @on(Button.Pressed, "#send-btn")
    def on_send(self) -> None:
        self._submit()

    @on(Input.Submitted, "#user-input")
    def on_input_submitted(self) -> None:
        self._submit()

    def _submit(self) -> None:
        if self._thinking:
            return
        input_widget = self.query_one("#user-input", Input)
        message = input_widget.value.strip()
        if not message:
            return
        input_widget.value = ""
        self._log_user(message)
        self._run_agent(message)

    @work(thread=True)
    def _run_agent(self, message: str) -> None:
        """
        Run the agent in a background thread so the TUI stays responsive.
        CrewAI is synchronous, so we use Textual's thread worker.
        """
        self._thinking = True
        self._cancel_event = asyncio.Event()
        self.call_from_thread(self._set_input_enabled, False)
        self.call_from_thread(
            self.query_one("#status-bar", StatusBar).set_state,
            "Thinking…", "thinking"
        )

        try:
            from agent import chat  # import here to keep startup fast
            response = chat(self._agent, self._history, message)
            self.call_from_thread(self._log_agent, response)
            self.call_from_thread(
                self.query_one("#status-bar", StatusBar).set_state,
                "Ready"
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("Agent error during chat: %s", exc, exc_info=True)
            self.call_from_thread(self._log_error, str(exc))
            self.call_from_thread(
                self.query_one("#status-bar", StatusBar).set_state,
                f"Error: {type(exc).__name__}", "error"
            )
        finally:
            self._thinking = False
            self.call_from_thread(self._set_input_enabled, True)
            self.call_from_thread(
                lambda: self.query_one("#user-input", Input).focus()
            )

    def action_clear_chat(self) -> None:
        self.query_one("#chat-log", RichLog).clear()
        self._history.clear()
        self._log_system("Chat cleared.")

    def action_cancel_request(self) -> None:
        """
        Cancel is a best-effort signal - CrewAI doesn't support mid-flight
        cancellation cleanly. This resets the UI state; the next response
        will be discarded.
        """
        if self._thinking:
            self._thinking = False
            self._set_input_enabled(True)
            self.query_one("#status-bar", StatusBar).set_state("Cancelled", "error")
            self._log_system("Request cancelled by user.")

    def action_confirm_exit(self) -> None:
        """Show the quit/restart confirmation dialog."""

        def _handle(choice: str) -> None:
            if choice == "quit":
                self.exit(0)
            elif choice == "restart":
                self.exit(EXIT_CODE_RESTART)
            # "cancel" → do nothing

        self.push_screen(ConfirmScreen("What would you like to do?"), _handle)

    def action_restart(self) -> None:
        """Restart immediately without confirmation."""
        self.exit(EXIT_CODE_RESTART)
