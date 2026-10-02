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
    tree = _build_tree(request.app.state.brain_notes)
    return templates.TemplateResponse(request, "brain_index.html", {"tree": tree})


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

# -----------------------------------------------------------------------------
# Private API
# -----------------------------------------------------------------------------
def _build_tree(notes: dict[str, dict]) -> dict:
    # Nest notes under their vault folders. Each node is
    # {name, folders, notes, count}, sorted by name, with count covering the
    # notes in every subfolder too.
    root = {"name": "", "folders": {}, "notes": [], "count": 0}
    for slug, note in notes.items():
        node = root
        node["count"] += 1
        for folder_name in note["folder"]:
            node = node["folders"].setdefault(
                folder_name, {"name": folder_name, "folders": {}, "notes": [], "count": 0}
            )
            node["count"] += 1
        node["notes"].append({"slug": slug, "title": note["title"], "tags": note["tags"]})

    def _sort(node: dict) -> dict:
        node["notes"].sort(key=lambda kwarg: kwarg["title"].lower())
        children = sorted(node["folders"].values(), key=lambda kwarg: kwarg["name"].lower())
        node["folders"] = [_sort(child) for child in children]
        return node

    return _sort(root)
