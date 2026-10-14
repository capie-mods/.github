"""Draws the organization avatar, the profile banner and the status badges.

The mark is "Overprint". When a state changed its name, post offices kept the old stamps and
overprinted them: parallel bars over the old country name, the new name printed above. CAPIE
and Rename Anything do the same to Hearts of Iron IV: the game's own object stays, a new name
goes over it. The stamp is parchment with an olive printed field (khaki frame and old name);
the strike bars are vermilion and the new name is brass. The whole overprint sits at a slight
angle, as hand-fed overprints did, but stays near horizontal so it never reads as a ban sign.

Colours come from the CAPIE design system (capie-design: tokens.json 1.2.0). Vermilion
(#b8432e) is one proposed brand-only extension for the overprint ink; it never marks state.
Flat fills only: no gradients, glow or shadows. One geometry feeds both the SVG and the PNG.

Two drawings:
    bold    few large notches, heavy bars, no inner frame. The GitHub avatar: GitHub shows it
            mostly at 20 to 48 px, where finer perforation turns to noise.
    detail  fine perforation and a khaki frame, for 128 px and up (banner tile, large prints)

Usage:
    python tools/make_assets.py           # writes profile/assets/*
    python tools/make_assets.py --check   # exit 1 if any file differs from a fresh render
"""

from __future__ import annotations

import argparse
import io
import math
import sys
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
"""Repository root."""

ASSETS = ROOT / "profile" / "assets"
"""Folder the profile README reads its pictures from."""

C = {
    "window-ink": "#0f0e0d",
    "field-ink": "#161412",
    "panel-umber": "#272421",
    "panel-rim": "#3c3936",
    "steel-bevel": "#76776b",
    "olive-button": "#2e3627",
    "brass": "#d0a070",
    "brass-dim": "#908060",
    "parchment": "#ece6d3",
    "khaki": "#c3b091",
    "header-amber": "#ffbd00",
    "go-green": "#7db35a",
    "caution-orange": "#ff7019",
    # Proposed brand-only extension: overprint ink. Never a state colour.
    "vermilion": "#b8432e",
    # Light page scheme of the documentation sites (sites/shared/theme/stylesheets/theme.css).
    "light-fg": "#1d1a17",
    "light-fg-2": "#4a443b",
}
"""Colour tokens (tokens.json 1.2.0), the vermilion extension and two light-scheme colours."""

GRID = 500
"""Edge of the drawing grid; the avatar is drawn 1:1 on it."""

TILT = -7.0
"""Overprint angle in degrees (negative rises to the right). Kept under 10 degrees."""


@dataclass(frozen=True)
class Shape:
    """One flat shape on the 500 grid.

    Attributes:
        kind: "rect" or "circle".
        colour: Token name.
        a: Rect left or circle centre x.
        b: Rect top or circle centre y.
        c: Rect right or circle radius.
        d: Rect bottom (unused for circles).
        tilted: True when the shape belongs to the overprint and turns by TILT.
    """

    kind: str
    colour: str
    a: float
    b: float
    c: float
    d: float = 0.0
    tilted: bool = False


@dataclass(frozen=True)
class Variant:
    """Proportions of one drawing."""

    stamp: tuple[float, float, float, float]
    teeth_x: int
    teeth_y: int
    tooth_r: float
    margin: float
    frame: float
    bar: float
    bar_gap: float
    name_h: float


DETAIL = Variant((116, 86, 384, 414), 8, 10, 12.5, 26, 5, 15, 13, 46)
"""Finely perforated stamp for 128 px and up."""

BOLD = Variant((112, 82, 388, 418), 4, 5, 22, 30, 0, 26, 20, 64)
"""Bold stamp for the avatar and every size under 128 px."""


def shapes(v: Variant) -> list[Shape]:
    """Builds the mark as a list of flat shapes, back to front."""
    x0, y0, x1, y1 = v.stamp
    out = [Shape("rect", "parchment", x0, y0, x1, y1)]
    for i in range(v.teeth_x + 1):
        x = x0 + (x1 - x0) * i / v.teeth_x
        out += [Shape("circle", "panel-umber", x, y0, v.tooth_r)]
        out += [Shape("circle", "panel-umber", x, y1, v.tooth_r)]
    for i in range(1, v.teeth_y):
        y = y0 + (y1 - y0) * i / v.teeth_y
        out += [Shape("circle", "panel-umber", x0, y, v.tooth_r)]
        out += [Shape("circle", "panel-umber", x1, y, v.tooth_r)]
    ix0, iy0, ix1, iy1 = x0 + v.margin, y0 + v.margin, x1 - v.margin, y1 - v.margin
    out.append(Shape("rect", "olive-button", ix0, iy0, ix1, iy1))
    if v.frame:
        f = 11
        for r in (
            (ix0 + f, iy0 + f, ix1 - f, iy0 + f + v.frame),
            (ix0 + f, iy1 - f - v.frame, ix1 - f, iy1 - f),
            (ix0 + f, iy0 + f, ix0 + f + v.frame, iy1 - f),
            (ix1 - f - v.frame, iy0 + f, ix1 - f, iy1 - f),
        ):
            out.append(Shape("rect", "khaki", *r))
    # Old country name, printed in khaki near the foot of the stamp.
    old_y = iy1 - 70 if v.frame else iy1 - 74
    old_h = 22 if v.frame else 30
    out.append(Shape("rect", "khaki", ix0 + 26, old_y, ix1 - 26, old_y + old_h))
    # Overprint: two parallel strike bars across the old name, wider than the printed field,
    # and the new name above them.
    mid = old_y + old_h / 2
    top = mid - v.bar_gap / 2 - v.bar
    out.append(Shape("rect", "vermilion", x0 + 4, top, x1 - 4, top + v.bar, tilted=True))
    bot = mid + v.bar_gap / 2
    out.append(Shape("rect", "vermilion", x0 + 4, bot, x1 - 4, bot + v.bar, tilted=True))
    name_bottom = top - (40 if v.frame else 34)
    out.append(
        Shape("rect", "brass", ix0 + 20, name_bottom - v.name_h, ix1 - 20, name_bottom, tilted=True)
    )
    return out


def turn(x: float, y: float) -> tuple[float, float]:
    """Rotates a point of the grid by TILT around the grid centre."""
    t = math.radians(TILT)
    cx = cy = GRID / 2
    dx, dy = x - cx, y - cy
    return (cx + dx * math.cos(t) - dy * math.sin(t), cy + dx * math.sin(t) + dy * math.cos(t))


def svg_shapes(v: Variant) -> str:
    """Returns the mark as SVG elements on the 500 grid."""
    plain: list[str] = []
    tilted: list[str] = []
    for s in shapes(v):
        if s.kind == "circle":
            el = f'<circle cx="{s.a:g}" cy="{s.b:g}" r="{s.c:g}" fill="{C[s.colour]}"/>'
        else:
            el = (
                f'<rect x="{s.a:g}" y="{s.b:g}" width="{s.c - s.a:g}" height="{s.d - s.b:g}" '
                f'fill="{C[s.colour]}"/>'
            )
        (tilted if s.tilted else plain).append(el)
    half = GRID / 2
    return (
        "".join(plain)
        + f'<g transform="rotate({TILT:g} {half:g} {half:g})">'
        + "".join(tilted)
        + "</g>"
    )


def avatar_svg(v: Variant, label: str) -> str:
    """Returns a square avatar SVG with a panel-umber ground."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {GRID} {GRID}" '
        f'width="{GRID}" height="{GRID}" role="img" aria-label="capie-mods">\n'
        f"  <!-- capie-mods mark, Overprint ({label}). Generated by tools/make_assets.py. -->\n"
        f'  <rect width="{GRID}" height="{GRID}" fill="{C["panel-umber"]}"/>\n'
        f"  {svg_shapes(v)}\n"
        "</svg>\n"
    )


def avatar_png(v: Variant, size: int) -> bytes:
    """Draws the avatar PNG with 4x supersampling from the same shapes as the SVG."""
    ss = 4
    k = size * ss / GRID
    img = Image.new("RGB", (size * ss, size * ss), C["panel-umber"])
    pen = ImageDraw.Draw(img)
    for s in shapes(v):
        if s.kind == "circle":
            pen.ellipse(
                ((s.a - s.c) * k, (s.b - s.c) * k, (s.a + s.c) * k, (s.b + s.c) * k),
                fill=C[s.colour],
            )
        elif s.tilted:
            corners = [turn(s.a, s.b), turn(s.c, s.b), turn(s.c, s.d), turn(s.a, s.d)]
            pen.polygon([(x * k, y * k) for x, y in corners], fill=C[s.colour])
        else:
            pen.rectangle((s.a * k, s.b * k, s.c * k - 1, s.d * k - 1), fill=C[s.colour])
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG", optimize=True)
    return buffer.getvalue()


FONT = "Ubuntu,'Segoe UI','DejaVu Sans',Verdana,sans-serif"
"""Design-system font stack; SVGs shown on GitHub cannot load web fonts."""


def banner_svg(*, dark: bool) -> str:
    """Returns the profile banner for one page scheme.

    The background is transparent so the banner sits on GitHub's own page colour. The mark
    keeps its panel-umber tile in both schemes, as diagrams keep their own canvas.
    """
    name = C["parchment"] if dark else C["light-fg"]
    sub = C["khaki"] if dark else C["light-fg-2"]
    tile = 128
    k = tile / GRID
    rim = "" if dark else f' stroke="{C["panel-rim"]}" stroke-width="1"'
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 160" width="880" height="160" '
        'role="img" aria-labelledby="t">\n'
        "  <title id=\"t\">capie-mods: CAPIE (Cyprian's API Extender) and the Hearts of Iron IV "
        "mods built on it</title>\n"
        f'  <rect x="0.5" y="16.5" width="{tile - 1}" height="{tile - 1}" rx="6" '
        f'fill="{C["panel-umber"]}"{rim}/>\n'
        f'  <g transform="translate(0 16) scale({k:g})">{svg_shapes(DETAIL)}</g>\n'
        f'  <text x="160" y="86" fill="{name}" style="font:700 60px {FONT};'
        'letter-spacing:.01em">CAPIE</text>\n'
        f'  <text x="162" y="124" fill="{sub}" style="font:400 22px {FONT}">'
        "Cyprian's API Extender, and the Hearts of Iron IV mods built on it</text>\n"
        "</svg>\n"
    )


BADGES = (
    ("HOI4", "1.19.3.0 ONLY", "go-green", "olive-button", False),
    ("STATUS", "BETA", "header-amber", "panel-umber", False),
    ("MULTIPLAYER", "NOT TESTED", "caution-orange", "panel-umber", False),
    ("SOURCE", "OPEN ON RELEASE", "brass", "panel-umber", True),
)
"""Badges: key, value, value text colour, value fill, planned (dashed rim)."""

CHAR = 7.0
"""Approximate advance of one 10 px bold capital with 0.08em tracking."""


def status_svg() -> tuple[str, int]:
    """Returns the badge row and its width."""
    parts: list[str] = []
    x = 1.0
    for key, value, ink, fill, planned in BADGES:
        kw = 16 + CHAR * len(key)
        vw = 16 + CHAR * len(value)
        w = kw + vw
        rim = (
            f'stroke="{C["brass-dim"]}" stroke-dasharray="5 4"'
            if planned
            else f'stroke="{C["panel-rim"]}"'
        )
        parts.append(
            f'<g transform="translate({x:g} 1)">'
            f'<rect width="{w:g}" height="22" rx="2" fill="{C["field-ink"]}"/>'
            f'<rect x="{kw:g}" width="{vw:g}" height="22" fill="{C[fill]}"/>'
            f'<rect x=".5" y=".5" width="{w - 1:g}" height="21" rx="2" fill="none" {rim} '
            'stroke-width="1"/>'
            f'<text x="8" y="15" fill="{C["parchment"]}">{key}</text>'
            f'<text x="{kw + 8:g}" y="15" fill="{C[ink]}">{value}</text></g>'
        )
        x += w + 8
    width = round(x - 7)
    desc = ". ".join(f"{k.capitalize()}: {v.lower()}" for k, v, *_ in BADGES) + "."
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} 24" width="{width}" '
        'height="24" role="img" aria-labelledby="t d">\n'
        '  <title id="t">Project status</title>\n'
        f'  <desc id="d">{desc}</desc>\n'
        "  <!-- Badge style of the CAPIE design system: one neutral rim, the state in the value "
        "text colour, a dashed brass-dim rim for planned. -->\n"
        f'  <g style="font:700 10px {FONT};letter-spacing:.08em">\n    '
        + "\n    ".join(parts)
        + "\n  </g>\n</svg>\n"
    )
    return svg, width


def plan() -> dict[Path, bytes]:
    """Returns every output file with its bytes."""
    status, _ = status_svg()
    return {
        ASSETS / "org-avatar.svg": avatar_svg(BOLD, "bold, the avatar").encode(),
        ASSETS / "org-avatar.png": avatar_png(BOLD, GRID),
        ASSETS / "org-mark-detail.svg": avatar_svg(DETAIL, "detail, 128 px and up").encode(),
        ASSETS / "org-mark-detail.png": avatar_png(DETAIL, GRID),
        ASSETS / "banner-dark.svg": banner_svg(dark=True).encode(),
        ASSETS / "banner-light.svg": banner_svg(dark=False).encode(),
        ASSETS / "status.svg": status.encode(),
    }


def main() -> int:
    """Writes or checks the assets."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="exit 1 when a file is stale")
    args = parser.parse_args()
    stale = 0
    for path, data in plan().items():
        if args.check:
            same = path.exists() and path.read_bytes() == data
            stale += not same
            print("UP-TO-DATE" if same else "STALE", path.relative_to(ROOT))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            print(f"Wrote {path.relative_to(ROOT)} ({len(data)} bytes)")
    return 1 if stale else 0


if __name__ == "__main__":
    sys.exit(main())
