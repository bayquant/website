# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
# Third-party imports
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

# Local imports
from ..render import templates

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


@router.get("/health")
async def health():
    return {"status": "ok"}
