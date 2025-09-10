"""Next-generation mapping module (experimental). Self-contained; does not modify existing code.

Public entry points:
- nextgen.taxonomy.load_taxonomy
- nextgen.agent.NextGenAimriMapper
- nextgen.cli: CLI for CSV batch mapping
"""

__all__ = [
    "NextGenAimriMapper",
    "load_taxonomy",
]

from .taxonomy import load_taxonomy  # noqa: E402
from .agent import NextGenAimriMapper  # noqa: E402

