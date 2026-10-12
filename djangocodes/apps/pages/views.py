"""Views for content pages."""

from __future__ import annotations

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from apps.core.views import trust_strip_context
from apps.pages.models import BlockType, Page
from apps.seo import schema


def render_page(request: HttpRequest, page: Page) -> HttpResponse:
    """Render a ``Page`` with its blocks (called by the slug dispatcher).

    Args:
        request: Current request.
        page: Published page with ``blocks`` prefetched.

    Returns:
        Rendered response.
    """
    blocks = list(page.blocks.all())
    faq_entries = [
        entry
        for block in blocks
        if block.block_type == BlockType.FAQ
        for entry in block.faq_entries
    ]
    context = {
        "page": page,
        "seo": page,
        "blocks": blocks,
        "breadcrumbs": [("Home", "/"), (page.title, page.get_absolute_url())],
        "schema_graph": [
            schema.breadcrumbs([("Home", "/"), (page.title, page.get_absolute_url())]),
            schema.faq_page(faq_entries),
        ],
        "audience": page.audience_note,
        **trust_strip_context(),
    }
    return render(request, f"pages/page_{page.template}.html", context)
