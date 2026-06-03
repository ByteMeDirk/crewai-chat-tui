"""
knowledge.py - Load a local knowledge base from files on disk.

All files in the configured knowledge directory are read and concatenated
into a single string that is injected into the agent's context/backstory.
This is intentionally simple - for larger KBs, replace with a vector store.
"""
from pathlib import Path

from config import CFG


def load_knowledge_base() -> str:
    """
    Read all knowledge files and return them as a single formatted string.
    Returns an empty string (with a note) if the directory is empty or missing.
    """
    kb_dir = Path(__file__).parent / CFG["knowledge"]["directory"]
    extensions = set(CFG["knowledge"]["file_extensions"])

    if not kb_dir.exists():
        return ""

    chunks: list[str] = []
    for path in sorted(kb_dir.iterdir()):
        if path.suffix in extensions and path.is_file():
            content = path.read_text(encoding="utf-8").strip()
            if content:
                chunks.append(f"=== {path.name} ===\n{content}")

    if not chunks:
        return ""

    return "\n\n".join(chunks)


def knowledge_summary() -> str:
    """Return a one-line status string for the TUI status bar."""
    kb_dir = Path(__file__).parent / CFG["knowledge"]["directory"]
    extensions = set(CFG["knowledge"]["file_extensions"])
    if not kb_dir.exists():
        return "KB: none"
    count = sum(
        1 for p in kb_dir.iterdir()
        if p.suffix in extensions and p.is_file()
    )
    return f"KB: {count} file{'s' if count != 1 else ''}"
