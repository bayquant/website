# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
# Standard library imports
import re
import tarfile
import urllib.error
import urllib.request
from io import BytesIO

# Third-party imports
import markdown

# -----------------------------------------------------------------------------
# Globals and constants
# -----------------------------------------------------------------------------
__all__ = ["load_brain_content"]

BRAIN_TARBALL_URL = "https://codeload.github.com/bayquant/brain/tar.gz/refs/heads/main"
BRAIN_CSS_PATH = ".obsidian/snippets/brain.css"

_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.DOTALL)
_TAGS_RE = re.compile(r"tags:\s*\[(.*?)\]")
_WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")
_LEADING_H1_RE = re.compile(r"^\s*<h1>.*?</h1>\s*", re.DOTALL)

# -----------------------------------------------------------------------------
# General API
# -----------------------------------------------------------------------------
def load_brain_content() -> tuple[dict[str, dict], str]:
    # Download the bayquant/brain repo as a tarball and turn every markdown note
    # into rendered HTML. Returns a mapping of slug -> {title, tags, html} and
    # the vault's brain.css rewritten to target the .note-content wrapper.
    with urllib.request.urlopen(BRAIN_TARBALL_URL, timeout=15) as response:
        archive_bytes = response.read()

    raw_notes: dict[str, dict] = {}
    css_text = ""

    with tarfile.open(fileobj=BytesIO(archive_bytes)) as tar:
        for member in tar.getmembers():
            if not member.isfile():
                continue
            # Strip the leading "<repo>-<branch>/" component from the tarball path.
            relative_path = member.name.split("/", 1)[1] if "/" in member.name else member.name

            if relative_path == BRAIN_CSS_PATH:
                css_text = tar.extractfile(member).read().decode("utf-8")
                continue

            if not relative_path.endswith(".md") or relative_path.startswith(".obsidian/"):
                continue

            content = tar.extractfile(member).read().decode("utf-8")
            tags, body = _parse_frontmatter(content)
            title = relative_path.rsplit("/", 1)[-1][: -len(".md")]
            slug = _path_to_slug(relative_path)
            raw_notes[slug] = {"title": title, "tags": tags, "body": body}

    notes = _render_notes(raw_notes)
    brain_css = css_text.replace(".markdown-preview-view", ".note-content")
    return notes, brain_css

# -----------------------------------------------------------------------------
# Private API
# -----------------------------------------------------------------------------
def _slugify(segment: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", segment.lower()).strip("-")


def _path_to_slug(relative_path: str) -> str:
    parts = relative_path[: -len(".md")].split("/")
    return "/".join(_slugify(part) for part in parts)


def _parse_frontmatter(text: str) -> tuple[list[str], str]:
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return [], text
    frontmatter, body = match.group(1), match.group(2)
    tags_match = _TAGS_RE.search(frontmatter)
    tags = []
    if tags_match:
        tags = [tag.strip() for tag in tags_match.group(1).split(",") if tag.strip()]
    return tags, body


def _render_notes(raw_notes: dict[str, dict]) -> dict[str, dict]:
    # Resolve [[wiki-links]] against note titles, convert bodies to HTML, and
    # drop the leading H1 the vault convention repeats inside every note.
    title_to_slug = {note["title"].lower(): slug for slug, note in raw_notes.items()}

    def _resolve_wikilink(match: re.Match) -> str:
        target = match.group(1).strip()
        display = (match.group(2) or target).strip()
        target_slug = title_to_slug.get(target.lower())
        if target_slug is None:
            return display
        return f"[{display}](/brain/{target_slug})"

    notes: dict[str, dict] = {}
    for slug, note in raw_notes.items():
        body_with_links = _WIKILINK_RE.sub(_resolve_wikilink, note["body"])
        html_body = markdown.markdown(body_with_links, extensions=["extra"])
        html_body = _LEADING_H1_RE.sub("", html_body, count=1)
        notes[slug] = {"title": note["title"], "tags": note["tags"], "html": html_body}
    return notes
