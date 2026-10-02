# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
# Standard library imports
import re
import tarfile
import urllib.error
import urllib.request
from io import BytesIO
from pathlib import PurePosixPath
from urllib.parse import quote

# Third-party imports
import markdown

# -----------------------------------------------------------------------------
# Globals and constants
# -----------------------------------------------------------------------------
__all__ = ["ATTACHMENT_TYPES", "load_brain_content"]

BRAIN_TARBALL_URL = "https://codeload.github.com/bayquant/brain/tar.gz/refs/heads/main"
ATTACHMENT_TYPES = {
    ".gif": "image/gif",
    ".jpeg": "image/jpeg",
    ".jpg": "image/jpeg",
    ".png": "image/png",
    ".svg": "image/svg+xml",
    ".webp": "image/webp",
}

_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.DOTALL)
_TAGS_RE = re.compile(r"tags:\s*\[(.*?)\]")
_EMBED_RE = re.compile(r"!\[\[([^\]|]+)(?:\|[^\]]*)?\]\]")
_WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")
_LEADING_H1_RE = re.compile(r"^\s*<h1>.*?</h1>\s*", re.DOTALL)

# -----------------------------------------------------------------------------
# General API
# -----------------------------------------------------------------------------
def load_brain_content() -> tuple[dict[str, dict], dict[str, bytes]]:
    # Download the bayquant/brain repo as a tarball and turn every markdown note
    # into rendered HTML. Returns a mapping of slug -> {title, tags, folder, html}
    # and a mapping of file name -> bytes for the images the notes embed.
    with urllib.request.urlopen(BRAIN_TARBALL_URL, timeout=15) as response:
        archive_bytes = response.read()

    raw_notes: dict[str, dict] = {}
    attachments: dict[str, bytes] = {}
    # The vault root is the directory holding .obsidian/ ("brain/" in this repo).
    vault_root = ""

    with tarfile.open(fileobj=BytesIO(archive_bytes)) as tar:
        for member in tar.getmembers():
            if not member.isfile():
                continue
            # Strip the leading "<repo>-<branch>/" component from the tarball path.
            relative_path = member.name.split("/", 1)[1] if "/" in member.name else member.name

            if ".obsidian/" in relative_path:
                vault_root = relative_path.split(".obsidian/", 1)[0]

            # Obsidian resolves ![[embeds]] by file name anywhere in the vault,
            # so attachments are keyed by bare name, not path.
            file_name = relative_path.rsplit("/", 1)[-1]
            if PurePosixPath(file_name).suffix.lower() in ATTACHMENT_TYPES:
                attachments[file_name] = tar.extractfile(member).read()
                continue

            if not relative_path.endswith(".md") or relative_path.startswith(".obsidian/"):
                continue

            content = tar.extractfile(member).read().decode("utf-8")
            tags, body = _parse_frontmatter(content)
            title = relative_path.rsplit("/", 1)[-1][: -len(".md")]
            slug = _path_to_slug(relative_path)
            raw_notes[slug] = {"title": title, "tags": tags, "path": relative_path, "body": body}

    # Folder names from the vault root down, e.g. ("Quant Finance",); () at the root.
    for note in raw_notes.values():
        vault_path = note.pop("path").removeprefix(vault_root)
        note["folder"] = tuple(vault_path.split("/")[:-1])

    notes = _render_notes(raw_notes, attachments)
    return notes, attachments

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


def _render_notes(raw_notes: dict[str, dict], attachments: dict[str, bytes]) -> dict[str, dict]:
    # Resolve ![[embeds]] and [[wiki-links]], convert bodies to HTML, and drop
    # the leading H1 the vault convention repeats inside every note.
    title_to_slug = {note["title"].lower(): slug for slug, note in raw_notes.items()}

    def _resolve_embed(match: re.Match) -> str:
        file_name = match.group(1).strip()
        if file_name not in attachments:
            return file_name
        return f"![{file_name}](/brain/assets/{quote(file_name)})"

    def _resolve_wikilink(match: re.Match) -> str:
        target = match.group(1).strip()
        display = (match.group(2) or target).strip()
        target_slug = title_to_slug.get(target.lower())
        if target_slug is None:
            return display
        return f"[{display}](/brain/{target_slug})"

    notes: dict[str, dict] = {}
    for slug, note in raw_notes.items():
        # Embeds go first, or the wiki-link pass would consume their [[...]].
        body_with_embeds = _EMBED_RE.sub(_resolve_embed, note["body"])
        body_with_links = _WIKILINK_RE.sub(_resolve_wikilink, body_with_embeds)
        # arithmatex shields $...$ and $$...$$ from markdown and leaves \(...\)
        # and \[...\] for KaTeX to render in the browser.
        html_body = markdown.markdown(
            body_with_links,
            extensions=["extra", "pymdownx.arithmatex"],
            extension_configs={"pymdownx.arithmatex": {"generic": True}},
        )
        html_body = _LEADING_H1_RE.sub("", html_body, count=1)
        notes[slug] = {
            "title": note["title"],
            "tags": note["tags"],
            "folder": note["folder"],
            "html": html_body,
        }
    return notes
