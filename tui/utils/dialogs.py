"""The TUIs Dialogs."""

from __future__ import annotations

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Label,
)


class ConfirmScreen(ModalScreen[str]):
    """
    A modal that asks the user to confirm quit or restart.
    Returns "quit", "restart", or "cancel".
    """

    DEFAULT_CSS = """
        ConfirmScreen {
            align: center middle;
        }
        #dialog {
            width: 50;
            height: auto;
            border: solid $primary;
            background: $surface;
            padding: 1 2;
        }
        #dialog Label {
            width: 100%;
            text-align: center;
            margin-bottom: 1;
        }
        #btn-row {
            width: 100%;
            height: auto;
            align: center middle;
        }
        #btn-row Button {
            margin: 0 1;
        }
    """

    def __init__(self, message: str) -> None:
        super().__init__()
        self._message = message

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label(self._message)
            with Horizontal(id="btn-row"):
                yield Button("Quit", id="btn-quit", variant="error")
                yield Button("Restart", id="btn-restart", variant="warning")
                yield Button("Cancel", id="btn-cancel", variant="default")

    @on(Button.Pressed, "#btn-quit")
    def _quit(self) -> None:
        self.dismiss("quit")

    @on(Button.Pressed, "#btn-restart")
    def _restart(self) -> None:
        self.dismiss("restart")

    @on(Button.Pressed, "#btn-cancel")
    def _cancel(self) -> None:
        self.dismiss("cancel")
