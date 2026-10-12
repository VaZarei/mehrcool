"""Responsive image renditions generated with Pillow and cached on disk.

Renditions live under ``MEDIA_ROOT/renditions/<key>/<width>.<format>`` and are created
lazily the first time a template asks for them. Changing the source file changes the
key, so stale renditions are never served.
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageOps, features

from django.conf import settings
from django.core.cache import cache
from django.core.files.storage import default_storage
from django.db.models.fields.files import FieldFile

logger = logging.getLogger(__name__)

RENDITION_DIR = "renditions"
DEFAULT_WIDTHS = (480, 768, 1080, 1440, 1920)
WEBP_QUALITY = 78
AVIF_QUALITY = 55
JPEG_QUALITY = 82
AVIF_SUPPORTED = features.check("avif")
_DIMENSION_CACHE_PREFIX = "core:imgdim:"
_DIMENSION_CACHE_SECONDS = 60 * 60 * 24


@dataclass(frozen=True)
class Rendition:
    """A generated image variant.

    Attributes:
        url: Public URL of the rendition.
        width: Pixel width.
        height: Pixel height.
        mime: MIME type such as ``image/webp``.
    """

    url: str
    width: int
    height: int
    mime: str


def is_vector(field: FieldFile) -> bool:
    """Whether the file is an SVG (which we never rasterise).

    Args:
        field: Image/file field.

    Returns:
        ``True`` for ``.svg`` files.
    """
    return (field.name or "").lower().endswith(".svg")


def _source_key(field: FieldFile) -> str:
    """Short hash identifying a specific version of the source file.

    Args:
        field: Source file field.

    Returns:
        16-character hex digest based on the name, size and modification time.
    """
    try:
        stat = default_storage.get_modified_time(field.name).timestamp()
        size = default_storage.size(field.name)
    except (OSError, NotImplementedError):
        stat, size = 0, 0
    raw = f"{field.name}:{size}:{stat}".encode()
    return hashlib.sha1(raw).hexdigest()[:16]


def source_dimensions(field: FieldFile) -> tuple[int, int] | None:
    """Return ``(width, height)`` of the source image, cached.

    Args:
        field: Source image field.

    Returns:
        Dimensions, or ``None`` if the image cannot be read.
    """
    if not field or is_vector(field):
        return None
    key = f"{_DIMENSION_CACHE_PREFIX}{_source_key(field)}"
    dims = cache.get(key)
    if dims is None:
        try:
            with default_storage.open(field.name, "rb") as fh, Image.open(fh) as img:
                dims = img.size
        except (OSError, ValueError) as exc:
            logger.warning("Could not read image %s: %s", field.name, exc)
            return None
        cache.set(key, dims, _DIMENSION_CACHE_SECONDS)
    return dims


def _rendition_relpath(field: FieldFile, width: int, fmt: str) -> str:
    """Relative storage path for a rendition.

    Args:
        field: Source field.
        width: Target width.
        fmt: ``webp``, ``avif`` or ``jpeg``.

    Returns:
        Path relative to ``MEDIA_ROOT``.
    """
    return f"{RENDITION_DIR}/{_source_key(field)}/{width}.{fmt}"


def get_rendition(field: FieldFile, width: int, fmt: str = "webp") -> Rendition | None:
    """Return (generating if needed) a resized rendition of ``field``.

    Args:
        field: Source image field.
        width: Desired width in pixels; never upscaled beyond the source.
        fmt: Output format: ``webp``, ``avif`` or ``jpeg``.

    Returns:
        The rendition, or ``None`` if the source is missing or vector.
    """
    if not field or is_vector(field):
        return None
    if fmt == "avif" and not AVIF_SUPPORTED:
        return None
    dims = source_dimensions(field)
    if dims is None:
        return None
    src_w, src_h = dims
    width = min(width, src_w)
    height = round(src_h * width / src_w)
    relpath = _rendition_relpath(field, width, fmt)
    mime = {"webp": "image/webp", "avif": "image/avif", "jpeg": "image/jpeg"}[fmt]

    if not default_storage.exists(relpath):
        try:
            _generate(field, relpath, width, fmt)
        except (OSError, ValueError) as exc:
            logger.warning("Rendition failed for %s: %s", field.name, exc)
            return None
    return Rendition(url=default_storage.url(relpath), width=width, height=height, mime=mime)


def _generate(field: FieldFile, relpath: str, width: int, fmt: str) -> None:
    """Create the rendition file on disk.

    Args:
        field: Source field.
        relpath: Destination relative path.
        width: Target width.
        fmt: Output format.
    """
    dest = Path(settings.MEDIA_ROOT) / relpath
    dest.parent.mkdir(parents=True, exist_ok=True)
    with default_storage.open(field.name, "rb") as fh, Image.open(fh) as img:
        img = ImageOps.exif_transpose(img)
        if fmt == "jpeg" and img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        elif img.mode not in ("RGB", "RGBA", "L"):
            img = img.convert("RGBA")
        ratio = width / img.width
        img = img.resize((width, max(1, round(img.height * ratio))), Image.Resampling.LANCZOS)
        save_kwargs: dict[str, object] = {"optimize": True}
        if fmt == "webp":
            save_kwargs = {"quality": WEBP_QUALITY, "method": 5}
        elif fmt == "avif":
            save_kwargs = {"quality": AVIF_QUALITY}
        else:
            save_kwargs = {"quality": JPEG_QUALITY, "optimize": True, "progressive": True}
        img.save(dest, format=fmt.upper(), **save_kwargs)


def srcset(field: FieldFile, widths: tuple[int, ...] | list[int], fmt: str) -> str:
    """Build a ``srcset`` string for the given widths.

    Args:
        field: Source image field.
        widths: Candidate widths.
        fmt: Output format.

    Returns:
        ``'url 480w, url 768w'`` style string (may be empty).
    """
    parts = []
    seen: set[int] = set()
    for w in sorted(set(widths)):
        rendition = get_rendition(field, w, fmt)
        if rendition and rendition.width not in seen:
            seen.add(rendition.width)
            parts.append(f"{rendition.url} {rendition.width}w")
    return ", ".join(parts)
