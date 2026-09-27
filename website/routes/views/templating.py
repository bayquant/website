# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
# Standard library imports
from pathlib import Path

# Third-party imports
from fastapi.templating import Jinja2Templates

# -----------------------------------------------------------------------------
# Globals and constants
# -----------------------------------------------------------------------------
__all__ = ["templates"]

_TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "templates"

# -----------------------------------------------------------------------------
# General API
# -----------------------------------------------------------------------------
# Shared Jinja2 environment used by every view to render website/templates/.
templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))
