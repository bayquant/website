# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
# Third-party imports
from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse

# Local imports
from .templating import templates

# -----------------------------------------------------------------------------
# Globals and constants
# -----------------------------------------------------------------------------
__all__ = ["router"]

router = APIRouter()

# -----------------------------------------------------------------------------
# General API
# -----------------------------------------------------------------------------
@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(request, "index.html")
