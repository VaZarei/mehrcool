"""Generate ``static/css/08-preferences.css`` from the other CSS layers.

The stylesheet holds literal values, not custom properties, so there is no
``:root`` block in which to re-declare durations, materials and border colours
for ``prefers-reduced-motion``, ``prefers-reduced-transparency`` and
``prefers-contrast``. This script walks the layers in ``main.css`` order and
emits one explicit override per affected selector instead.

Run it after adding or changing a transition, a blurred surface or a hairline
border, then run ``manage.py build_css``:

    python scripts/gen_preferences.py

It rewrites the file wholesale, so put hand edits in a component layer rather
than in the generated file.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

CSS_DIR = Path(__file__).resolve().parent.parent / "static" / "css"
ORDER_RE = re.compile(r'@import\s+url\(["\']?([^"\')]+)["\']?\);')
OUTPUT_NAME = "08-preferences.css"

# Flattened value -> high-contrast replacement (was a :root swap under
# prefers-contrast: more).
CONTRAST_SWAPS = {
    "#e1e4ea": "#737b8a",  # border-subtle  -> grey-500
    "#c3c8d1": "#3d4350",  # border-strong  -> grey-700
    "#58606f": "#262a33",  # text-secondary -> grey-800
    "rgb(255 255 255 / 0.72)": "#ffffff",  # text-on-dark-muted -> white
}

# Translucent surfaces become solid under prefers-reduced-transparency. Values
# not listed here just lose their blur; the background is left alone.
TRANSPARENCY_SWAPS = {
    "rgb(255 255 255 / 0.78)": "#ffffff",
    "rgb(255 255 255 / 0.96)": "#ffffff",
    "rgb(21 31 71 / 0.72)": "#151f47",
    "rgb(21 31 71 / 0.5)": "#151f47",
    "rgb(255 255 255 / 0.12)": "#34499e",
    "rgb(255 255 255 / 0.08)": "#34499e",
}


def rules(css: str) -> list[tuple[str, str]]:
    """Return (selector, body) pairs, flattening one level of at-rules.

    @keyframes bodies are skipped: their `from`/`to` blocks are not selectors.
    """
    out: list[tuple[str, str]] = []
    i = 0
    while i < len(css):
        brace = css.find("{", i)
        if brace == -1:
            break
        prelude = css[i:brace].strip()
        depth, j = 1, brace + 1
        while j < len(css) and depth:
            depth += (css[j] == "{") - (css[j] == "}")
            j += 1
        body = css[brace + 1 : j - 1]
        if prelude.startswith("@"):
            if not prelude.startswith(("@keyframes", "@font-face")):
                out.extend(rules(body))
        else:
            out.append((prelude, body))
        i = j
    return out


def declarations(body: str) -> list[tuple[str, str]]:
    out = []
    for chunk in body.split(";"):
        if ":" in chunk:
            prop, _, value = chunk.partition(":")
            out.append((prop.strip(), re.sub(r"\s+", " ", value).strip()))
    return out


def clean_selector(selector: str) -> str:
    selector = re.sub(r"/\*.*?\*/", "", selector, flags=re.S).strip()
    return re.sub(r"\s*,\s*", ",\n", re.sub(r"\s+", " ", selector))


def main() -> int:
    files = [
        f
        for f in ORDER_RE.findall((CSS_DIR / "main.css").read_text(encoding="utf-8"))
        if f != OUTPUT_NAME
    ]
    motion: list[str] = []
    contrast: list[str] = []
    transparency: list[str] = []
    seen_motion: set[str] = set()
    seen_transparency: set[str] = set()

    for name in files:
        css = (CSS_DIR / name).read_text(encoding="utf-8")
        css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
        for selector, body in rules(css):
            decls = declarations(body)
            selector = clean_selector(selector)
            if not selector:
                continue

            props = [p for p, _ in decls]
            has_transition = any(p == "transition" or p.startswith("transition-") for p in props)
            has_animation = any(p == "animation" or p.startswith("animation-") for p in props)
            if (has_transition or has_animation) and selector not in seen_motion:
                seen_motion.add(selector)
                lines = []
                if has_transition:
                    lines.append("  transition-duration: 0s;")
                    lines.append("  transition-delay: 0s;")
                if has_animation:
                    lines.append("  animation-duration: 0s;")
                    lines.append("  animation-delay: 0s;")
                motion.append(f"{selector} {{\n" + "\n".join(lines) + "\n}")

            if any(p.endswith("backdrop-filter") for p, _ in decls) and (
                selector not in seen_transparency
            ):
                seen_transparency.add(selector)
                lines = ["  -webkit-backdrop-filter: none;", "  backdrop-filter: none;"]
                for prop, value in decls:
                    if prop in ("background", "background-color") and value in TRANSPARENCY_SWAPS:
                        lines.append(f"  {prop}: {TRANSPARENCY_SWAPS[value]};")
                transparency.append(f"{selector} {{\n" + "\n".join(lines) + "\n}")

            swapped = []
            for prop, value in decls:
                if prop.startswith("--"):
                    continue
                new = value
                for old, repl in CONTRAST_SWAPS.items():
                    new = new.replace(old, repl)
                if new != value:
                    swapped.append(f"  {prop}: {new};")
            if swapped:
                contrast.append(f"{selector} {{\n" + "\n".join(swapped) + "\n}")

    header = (
        "/* ==========================================================================\n"
        "   08 — User preference overrides\n"
        "   GENERATED FILE — do not edit. Run scripts/gen_preferences.py after\n"
        "   changing a transition, a blurred surface or a hairline border.\n"
        "   There is no :root block to re-declare, so each affected selector gets\n"
        "   an explicit override here. Loaded last, to win on equal specificity.\n"
        "   ========================================================================== */\n"
    )
    body = [header]
    body.append(
        "\n/* --- Reduced motion ------------------------------------------------------\n"
        "   Feedback is kept (colour, opacity end states); the travel is removed. */\n"
        "@media (prefers-reduced-motion: reduce) {\n"
        + "\n\n".join(re.sub(r"^", "  ", r, flags=re.M) for r in motion)
        + "\n}\n"
    )
    body.append(
        "\n/* --- Reduced transparency ------------------------------------------------\n"
        "   Glass becomes a solid surface: the blur is dropped and the known\n"
        "   translucent fills are replaced with their opaque equivalents. */\n"
        "@media (prefers-reduced-transparency: reduce) {\n"
        + "\n\n".join(re.sub(r"^", "  ", r, flags=re.M) for r in transparency)
        + "\n}\n"
    )
    body.append(
        "\n/* --- Increased contrast --------------------------------------------------\n"
        "   Hairlines and secondary text step up two ramp stops. */\n"
        "@media (prefers-contrast: more) {\n"
        + "\n\n".join(re.sub(r"^", "  ", r, flags=re.M) for r in contrast)
        + "\n}\n"
    )
    (CSS_DIR / OUTPUT_NAME).write_text("".join(body), encoding="utf-8")
    print(
        f"{len(motion)} motion, {len(transparency)} transparency, "
        f"{len(contrast)} contrast overrides"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
