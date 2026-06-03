"""
config.py - Load and expose application configuration from config.yaml.
"""
from pathlib import Path
import yaml

_CONFIG_PATH = Path(__file__).parent / "config.yaml"


def load_config() -> dict:
    """Load the YAML config file and return it as a plain dict."""
    with open(_CONFIG_PATH) as f:
        return yaml.safe_load(f)


# Module-level singleton so other modules can do: from config import CFG
CFG = load_config()
