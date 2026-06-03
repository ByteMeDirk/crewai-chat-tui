"""The TUIs Widgets."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widgets import (
    Static,
)

from config import CFG
from knowledge import knowledge_summary


class StatusBar(Horizontal):
    """Bottom status bar showing model name, KB status, and agent state."""

    state: reactive[str] = reactive("Ready")
    state_class: reactive[str] = reactive("")

    def compose(self) -> ComposeResult:
        model = CFG["ollama"]["model"]
        yield Static(f"model: {model}", id="status-model")
        yield Static(knowledge_summary(), id="status-kb")
        yield Static("● Ready", id="status-state")

    def set_state(self, text: str, css_class: str = "") -> None:
        widget = self.query_one("#status-state", Static)
        widget.update(f"● {text}")
        widget.remove_class("thinking", "error")
        if css_class:
            widget.add_class(css_class)

    def set_kb(self, text: str) -> None:
        self.query_one("#status-kb", Static).update(text)
