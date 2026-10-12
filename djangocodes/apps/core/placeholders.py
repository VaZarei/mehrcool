"""Generate lightweight branded placeholder media (SVG, raster, video).

Everything produced here is a stand-in listed in ``ASSETS_NEEDED.md``. Files are
written under ``MEDIA_ROOT/placeholders/`` and attached to seeded objects.
"""

from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from django.conf import settings

logger = logging.getLogger(__name__)

NAVY = "#2B3E8C"
NAVY_DARK = "#151F47"
ICE = "#4A72C0"
ICE_LIGHT = "#A7BFE8"
AMBER = "#F29D12"
YELLOW = "#FFC82B"
WHITE = "#FFFFFF"
CHARCOAL = "#111111"

PLACEHOLDER_DIR = Path(settings.MEDIA_ROOT) / "placeholders"


def _write(name: str, content: str | bytes) -> Path:
    """Write a placeholder file and return its path.

    Args:
        name: File name relative to the placeholder directory.
        content: Text or bytes.

    Returns:
        Absolute path.
    """
    PLACEHOLDER_DIR.mkdir(parents=True, exist_ok=True)
    path = PLACEHOLDER_DIR / name
    if isinstance(content, str):
        path.write_text(content, encoding="utf-8")
    else:
        path.write_bytes(content)
    return path


def _mark_svg(size: int = 64, ring: str = NAVY) -> str:
    """Inner SVG group approximating the sun/snowflake mark.

    Args:
        size: Nominal size the mark is drawn into.
        ring: Ring colour.

    Returns:
        SVG fragment.
    """
    c = size / 2
    r = size * 0.42
    arms = []
    for angle in (0, 60, 120):
        arms.append(
            f'<line x1="{c}" y1="{c - r * 0.75}" x2="{c}" y2="{c + r * 0.75}" '
            f'transform="rotate({angle} {c} {c})" stroke="{ICE}" stroke-width="{size * 0.045}" '
            'stroke-linecap="round"/>'
        )
    return (
        f'<circle cx="{c}" cy="{c}" r="{r}" fill="none" stroke="{ring}" stroke-width="{size * 0.09}"/>'
        f'<path d="M{c} {c - r * 0.78} A{r * 0.78} {r * 0.78} 0 0 0 {c} {c + r * 0.78} Z" fill="{AMBER}"/>'
        f'<circle cx="{c - r * 0.25}" cy="{c}" r="{r * 0.28}" fill="{YELLOW}"/>' + "".join(arms)
    )


def logo_svg(dark_background: bool = False) -> str:
    """Horizontal logo: mark + 'MehrCool' wordmark + descriptor.

    Args:
        dark_background: Use white text for dark surfaces.

    Returns:
        SVG markup.
    """
    text = WHITE if dark_background else CHARCOAL
    accent = ICE_LIGHT if dark_background else NAVY
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 160" width="640" height="160" '
        'role="img" aria-label="Mehr Cool Refrigeration and Air Conditioning">'
        f'<g transform="translate(8 8)">{_mark_svg(144, ring=accent if dark_background else NAVY)}</g>'
        f'<text x="176" y="88" font-family="ui-sans-serif, -apple-system, Segoe UI, Inter, Arial, sans-serif" '
        f'font-size="68" font-weight="700" letter-spacing="-2" fill="{text}">Mehr<tspan fill="{accent}">Cool</tspan></text>'
        f'<text x="178" y="128" font-family="ui-sans-serif, -apple-system, Segoe UI, Inter, Arial, sans-serif" '
        f'font-size="22" font-weight="500" letter-spacing="3" fill="{text}" opacity="0.75">REFRIGERATION &amp; AIR CONDITIONING</text>'
        "</svg>"
    )


def favicon_svg() -> str:
    """Square favicon with the mark on navy.

    Returns:
        SVG markup.
    """
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">'
        f'<rect width="64" height="64" rx="14" fill="{NAVY}"/>'
        f'<g transform="translate(6 6) scale(0.8125)">{_mark_svg(64, ring=WHITE)}</g>'
        "</svg>"
    )


def badge_svg(label: str, sub: str = "", colour: str = NAVY) -> str:
    """Accreditation-style badge: rounded rectangle with a bold label.

    Args:
        label: Main text, e.g. ``'F-GAS'``.
        sub: Small caption, e.g. ``'CERTIFIED'``.
        colour: Background colour.

    Returns:
        SVG markup.
    """
    aria = f"{label} {sub}".strip()
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 128" width="320" height="128" '
        f'role="img" aria-label="{aria}">'
        f'<rect x="4" y="4" width="312" height="120" rx="20" fill="{colour}"/>'
        f'<text x="160" y="{68 if sub else 78}" text-anchor="middle" font-family="ui-sans-serif, -apple-system, Segoe UI, Arial, sans-serif" '
        f'font-size="44" font-weight="800" letter-spacing="-1" fill="{WHITE}">{label}</text>'
        + (
            f'<text x="160" y="100" text-anchor="middle" font-family="ui-sans-serif, -apple-system, Segoe UI, Arial, sans-serif" '
            f'font-size="18" font-weight="600" letter-spacing="3" fill="{WHITE}" opacity="0.85">{sub}</text>'
            if sub
            else ""
        )
        + "</svg>"
    )


def wordmark_svg(name: str, colour: str = "#3D4350") -> str:
    """Brand/client placeholder: plain wordmark.

    Args:
        name: Company name.
        colour: Text colour.

    Returns:
        SVG markup.
    """
    size = 44 if len(name) <= 10 else 34 if len(name) <= 16 else 26
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 96" width="320" height="96" '
        f'role="img" aria-label="{name}">'
        f'<text x="160" y="60" text-anchor="middle" font-family="ui-sans-serif, -apple-system, Segoe UI, Arial, sans-serif" '
        f'font-size="{size}" font-weight="700" letter-spacing="-0.5" fill="{colour}">{name}</text>'
        "</svg>"
    )


def _hex(colour: str) -> tuple[int, int, int]:
    """Convert ``#RRGGBB`` to an RGB tuple."""
    colour = colour.lstrip("#")
    return tuple(int(colour[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def scene_jpeg(
    name: str,
    width: int = 1600,
    height: int = 1000,
    start: str = NAVY_DARK,
    end: str = ICE,
    accent: str = AMBER,
    seed: int = 0,
) -> Path:
    """Raster placeholder: diagonal gradient with soft geometric 'equipment' shapes.

    Args:
        name: Output file name (``.jpg``).
        width: Pixel width.
        height: Pixel height.
        start: Gradient start colour.
        end: Gradient end colour.
        accent: Accent shape colour.
        seed: Varies the composition.

    Returns:
        Path to the written JPEG.
    """
    path = PLACEHOLDER_DIR / name
    if path.exists():
        return path
    PLACEHOLDER_DIR.mkdir(parents=True, exist_ok=True)
    s, e = _hex(start), _hex(end)
    base = Image.new("RGB", (width, height))
    px = base.load()
    for y in range(height):
        for x in range(0, width, 4):
            t = x / width * 0.6 + y / height * 0.4
            col = tuple(int(s[i] + (e[i] - s[i]) * t) for i in range(3))
            for dx in range(4):
                if x + dx < width:
                    px[x + dx, y] = col
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    rng = (seed * 9301 + 49297) % 233280
    for i in range(6):
        rng = (rng * 9301 + 49297) % 233280
        cx = int(width * (0.15 + 0.7 * ((rng / 233280 + i * 0.17) % 1)))
        rng = (rng * 9301 + 49297) % 233280
        cy = int(height * (0.2 + 0.6 * ((rng / 233280 + i * 0.31) % 1)))
        r = int(min(width, height) * (0.08 + 0.06 * (i % 3)))
        alpha = 26 + 12 * (i % 3)
        draw.rounded_rectangle(
            (cx - r, cy - r, cx + r, cy + int(r * 1.4)), radius=r // 4, fill=(255, 255, 255, alpha)
        )
    ax, ay = int(width * 0.78), int(height * 0.3)
    draw.ellipse((ax - 90, ay - 90, ax + 90, ay + 90), fill=(*_hex(accent), 110))
    overlay = overlay.filter(ImageFilter.GaussianBlur(3))
    base = Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")
    # Fine grid: suggests engineering drawings / grille.
    grid = ImageDraw.Draw(base)
    for gx in range(0, width, 80):
        grid.line((gx, 0, gx, height), fill=(255, 255, 255), width=1)
    for gy in range(0, height, 80):
        grid.line((0, gy, width, gy), fill=(255, 255, 255), width=1)
    base = Image.blend(base, base.filter(ImageFilter.GaussianBlur(0.6)), 0.5)
    base.save(path, "JPEG", quality=80, optimize=True, progressive=True)
    return path


def hero_video(duration: int = 8, size: str = "1280x720") -> tuple[Path | None, Path | None]:
    """Generate a short silent gradient MP4 + WebM with ffmpeg if available.

    Args:
        duration: Seconds.
        size: ``WxH``.

    Returns:
        ``(mp4_path, webm_path)``; either may be ``None`` if ffmpeg is missing or fails.
    """
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        logger.warning("ffmpeg not found; skipping hero video placeholder")
        return None, None
    PLACEHOLDER_DIR.mkdir(parents=True, exist_ok=True)
    mp4 = PLACEHOLDER_DIR / "hero-placeholder.mp4"
    webm = PLACEHOLDER_DIR / "hero-placeholder.webm"
    source = (
        f"gradients=s={size}:d={duration}:speed=0.015:nb_colors=3:"
        f"c0=0x{NAVY_DARK[1:]}:c1=0x{NAVY[1:]}:c2=0x{ICE[1:]},format=yuv420p"
    )
    filters = "noise=alls=6:allf=t+u,eq=contrast=1.05"
    jobs = [
        (mp4, ["-c:v", "libx264", "-preset", "veryfast", "-crf", "30", "-movflags", "+faststart"]),
        (
            webm,
            [
                "-c:v",
                "libvpx-vp9",
                "-b:v",
                "0",
                "-crf",
                "42",
                "-row-mt",
                "1",
                "-deadline",
                "realtime",
            ],
        ),
    ]
    results: list[Path | None] = []
    for out, codec in jobs:
        if out.exists():
            results.append(out)
            continue
        cmd = [
            ffmpeg,
            "-y",
            "-loglevel",
            "error",
            "-f",
            "lavfi",
            "-i",
            source,
            "-vf",
            filters,
            "-an",
            "-t",
            str(duration),
            *codec,
            str(out),
        ]
        try:
            subprocess.run(cmd, check=True, timeout=300)
            results.append(out)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as exc:
            logger.warning("ffmpeg failed for %s: %s", out.name, exc)
            results.append(None)
    return results[0], results[1]


def write_svg(name: str, svg: str) -> Path:
    """Write an SVG placeholder.

    Args:
        name: File name.
        svg: Markup.

    Returns:
        Path.
    """
    return _write(name, svg)
