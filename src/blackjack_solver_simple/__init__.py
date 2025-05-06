"""
Top-level package for blackjack_solver_simple.

Exposes the public API (core game objects & RL helpers) while
keeping heavier, optional deps (e.g. NiceGUI) out of the import path.
"""

from importlib.metadata import version as _pkg_version

# ── Re-export the essentials ──────────────────────────────────────────────
from .core import Card, Rank, Suit  # noqa: F401

__all__: list[str] = [
    "Card",
    "Rank",
    "Suit",
    "__version__",
]

# Package version (falls back gracefully if metadata missing)
try:
    __version__: str = _pkg_version(__name__)
except Exception:  # when running from a plain source tree
    __version__ = "0.0.0"
