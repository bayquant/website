# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
# Standard library imports
from pathlib import PurePosixPath

# Third-party imports
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import Response

# Local imports
from ...services.brain_content import ATTACHMENT_TYPES
from .templating import templates

# -----------------------------------------------------------------------------
# Globals and constants
# -----------------------------------------------------------------------------
__all__ = ["router"]

router = APIRouter(prefix="/brain")

# -----------------------------------------------------------------------------
# General API
# -----------------------------------------------------------------------------
@router.get("", response_class=HTMLResponse)
async def brain_index(request: Request):
    notes = request.app.state.brain_notes
    items = [
        {"slug": slug, "title": note["title"], "tags": note["tags"]}
        for slug, note in sorted(notes.items(), key=lambda kwarg: kwarg[1]["title"].lower())
    ]
    return templates.TemplateResponse(request, "brain_index.html", {"notes": items})


# Registered before the note route, whose {slug:path} would otherwise match it.
@router.get("/assets/{name}")
async def brain_attachment(request: Request, name: str):
    content = request.app.state.brain_attachments.get(name)
    if content is None:
        raise HTTPException(status_code=404, detail="Attachment not found")
    media_type = ATTACHMENT_TYPES[PurePosixPath(name).suffix.lower()]
    return Response(content, media_type=media_type)


@router.get("/{slug:path}", response_class=HTMLResponse)
async def brain_note(request: Request, slug: str):
    note = request.app.state.brain_notes.get(slug)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return templates.TemplateResponse(
        request,
        "brain_note.html",
        {"title": note["title"], "html": note["html"]},
    )
