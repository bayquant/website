#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
# Other imports
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

# Relative imports
from ..render import templates

#-----------------------------------------------------------------------------
# Globals and constants
#-----------------------------------------------------------------------------
__all__ = ["router"]

router = APIRouter(prefix="/brain")

#-----------------------------------------------------------------------------
# General API
#-----------------------------------------------------------------------------
@router.get("", response_class=HTMLResponse)
async def brain_index(request: Request):
    notes = request.app.state.brain_notes
    items = [
        {"slug": slug, "title": note["title"], "tags": note["tags"]}
        for slug, note in sorted(notes.items(), key=lambda kwarg: kwarg[1]["title"].lower())
    ]
    return templates.TemplateResponse(
        request,
        "brain_index.html",
        {"notes": items, "css": request.app.state.brain_css},
    )


@router.get("/{slug:path}", response_class=HTMLResponse)
async def brain_note(request: Request, slug: str):
    note = request.app.state.brain_notes.get(slug)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return templates.TemplateResponse(
        request,
        "brain_note.html",
        {"title": note["title"], "html": note["html"], "css": request.app.state.brain_css},
    )
