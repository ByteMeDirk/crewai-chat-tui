"""The TUIs Application CSS."""

APP_CSS = """
Screen {
    layers: base overlay;
}

#chat-container {
    height: 1fr;
    border: solid $primary-darken-2;
    padding: 0 1;
}

#chat-log {
    height: 1fr;
}

#input-row {
    height: 3;
    margin-top: 1;
    margin-bottom: 1;
}

#user-input {
    width: 1fr;
    margin-right: 1;
}

#send-btn {
    width: 8;
    min-width: 8;
}

#status-bar {
    height: 1;
    background: $primary-darken-3;
    color: $text-muted;
    padding: 0 1;
}

#status-model {
    width: auto;
    margin-right: 2;
}

#status-kb {
    width: auto;
    margin-right: 2;
}

#status-state {
    width: 1fr;
    text-align: right;
    color: $success;
}

#status-state.thinking {
    color: $warning;
}

#status-state.error {
    color: $error;
}

/* User messages */
.msg-user {
    color: $accent;
    margin-bottom: 0;
}

/* Assistant messages */
.msg-agent {
    color: $text;
    margin-bottom: 1;
}

/* Error messages inline in chat */
.msg-error {
    color: $error;
    margin-bottom: 1;
}

/* System/info messages */
.msg-system {
    color: $text-muted;
    text-style: italic;
    margin-bottom: 1;
}
"""
