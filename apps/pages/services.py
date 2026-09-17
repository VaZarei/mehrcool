"""Business logic for the pages app: block item parsing, text markup and index-page copy."""

from __future__ import annotations

import html
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .models import Page

ITEM_SEPARATOR = "::"

# Slugs whose Page rows hold the heading/intro/SEO for hand-built index pages
# (they are never served directly because explicit routes match first).
RESERVED_PAGE_SLUGS = {
    "services": "All services index",
    "sectors": "Sectors index",
    "case-studies": "Case studies index",
    "areas": "Areas we cover index",
    "contact": "Contact page",
    "emergency-callout": "Emergency callout page",
}


@dataclass
class PageCopy:
    """Editable heading/intro/blocks for a hand-built index page.

    Attributes:
        title: The H1.
        intro: Lead paragraph.
        page: The backing ``Page`` if one exists (used for SEO fields), else ``None``.
        blocks: Content blocks to render below the hard-built content.
    """

    title: str
    intro: str
    page: Page | None = None
    blocks: list[Any] = field(default_factory=list)


def page_copy(slug: str, default_title: str, default_intro: str = "") -> PageCopy:
    """Load admin-editable copy for an index page, with defaults if no Page exists.

    Args:
        slug: One of :data:`RESERVED_PAGE_SLUGS`.
        default_title: Fallback heading.
        default_intro: Fallback intro.

    Returns:
        A ``PageCopy`` the view can hand to the template.
    """
    from .models import Page

    page = (
        Page.objects.published()
        .prefetch_related("blocks__gallery_images")
        .filter(slug=slug)
        .first()
    )
    if page is None:
        return PageCopy(title=default_title, intro=default_intro)
    return PageCopy(
        title=page.title or default_title,
        intro=page.intro or default_intro,
        page=page,
        blocks=list(page.blocks.all()),
    )


_BOLD = re.compile(r"\*\*(.+?)\*\*")
_LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")


def parse_block_items(raw: str) -> list[dict[str, str]]:
    """Parse ``Title :: Body :: Link`` lines into dicts.

    Args:
        raw: The block's ``items`` text.

    Returns:
        A list of ``{'title', 'body', 'url'}`` dicts, skipping blank lines.
    """
    items: list[dict[str, str]] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split(ITEM_SEPARATOR)]
        parts += [""] * (3 - len(parts))
        items.append({"title": parts[0], "body": parts[1], "url": parts[2]})
    return items


def _inline(text: str) -> str:
    """Escape HTML then apply bold and link markup.

    Args:
        text: Raw inline text.

    Returns:
        Safe HTML fragment.
    """
    escaped = html.escape(text, quote=False)
    escaped = _BOLD.sub(r"<strong>\1</strong>", escaped)
    escaped = _LINK.sub(r'<a href="\2">\1</a>', escaped)
    return escaped


def render_text(raw: str) -> str:
    """Convert the admin's plain text into HTML paragraphs, lists and sub-headings.

    Supported syntax (kept deliberately tiny so a non-technical admin can learn it in a
    minute): blank line = paragraph break, ``- `` = bullet, ``## `` = sub-heading,
    ``**bold**`` and ``[text](url)`` links.

    Args:
        raw: Text as typed in the admin.

    Returns:
        HTML string (caller marks it safe).
    """
    out: list[str] = []
    paragraph: list[str] = []
    in_list = False

    def flush_paragraph() -> None:
        if paragraph:
            out.append(f"<p>{' '.join(_inline(p) for p in paragraph)}</p>")
            paragraph.clear()

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            out.append("</ul>")
            in_list = False

    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            close_list()
            continue
        if stripped.startswith("## "):
            flush_paragraph()
            close_list()
            out.append(f"<h3>{_inline(stripped[3:])}</h3>")
        elif stripped.startswith("### "):
            flush_paragraph()
            close_list()
            out.append(f"<h4>{_inline(stripped[4:])}</h4>")
        elif stripped.startswith(("- ", "* ")):
            flush_paragraph()
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{_inline(stripped[2:])}</li>")
        else:
            close_list()
            paragraph.append(stripped)
    flush_paragraph()
    close_list()
    return "\n".join(out)
