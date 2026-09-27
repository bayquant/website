# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
# Third-party imports
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

# Local imports
from . import brain
from . import home

# -----------------------------------------------------------------------------
# Globals and constants
# -----------------------------------------------------------------------------
__all__ = ["router"]

# Server-rendered HTML pages. Kept out of the OpenAPI schema.
router = APIRouter(
    default_response_class=HTMLResponse,
    include_in_schema=False,
    tags=["views"],
)
router.include_router(home.router)
router.include_router(brain.router)
