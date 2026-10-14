"""Draws the organization avatar, the profile banner and the status badges.

Every picture follows the CAPIE design system (capie-design: DESIGN-SYSTEM.md, tokens.json
1.2.0). The avatar is the CAPIE connector mark (three brass bars beside a field-ink plate with
a steel bevel) as drawn on the CAPIE switch mod thumbnail, centred on a panel-umber square and
sized so that GitHub's circular crop leaves it whole. Flat fills only: no gradients, glow or
shadows.

Usage:
    python tools/make_assets.py           # writes profile/assets/*
    python tools/make_assets.py --check   # exit 1 if any file differs from a fresh render
"""

from __future__ import annotations

import argparse
import io
import sys
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
    # Light page scheme of the documentation sites (sites/shared/theme/stylesheets/theme.css).
    "light-fg": "#1d1a17",
    "light-fg-2": "#4a443b",
}
"""Colour tokens (tokens.json 1.2.0) and the two derived light-scheme text colours."""

# Connector mark on the 512 px grid of the CAPIE switch mod thumbnail. The bars are 20 units
# tall instead of 16 so that they stay 3 px apart and visible at the 40 px avatar size.
PLATE = (92.0, 106.0, 196.0, 266.0)
"""Plate rectangle (left, top, right, bottom)."""

BAR_X = (48.0, 92.0)
"""Left and right edge of the three bars."""

BAR_CENTRES = (146.0, 186.0, 226.0)
"""Vertical centres of the three bars."""

BAR_HEIGHT = 20.0
"""Bar height."""

BEVEL = 4.0
"""Steel bevel stroke of the plate."""

MARK_CENTRE = ((BAR_X[0] + PLATE[2]) / 2, (PLATE[1] + PLATE[3]) / 2)
"""Centre of the mark's bounding box."""

AVATAR = 500
"""Avatar edge in pixels (GitHub recommends at least 500 x 500)."""

AVATAR_SCALE = 1.9
"""Mark scale on the avatar: the bounding box corners sit at 83 % of the crop radius."""


def mark_svg(scale: float, cx: float, cy: float) -> str:
    """Returns the connector mark as SVG elements centred on (cx, cy).

    Args:
        scale: Factor from the thumbnail grid to the target.
        cx: Horizontal centre on the target.
        cy: Vertical centre on the target.

    Returns:
        A <g> element.
    """
    tx = cx - MARK_CENTRE[0] * scale
    ty = cy - MARK_CENTRE[1] * scale
    half = BEVEL / 2
    bars = "".join(
        f'<rect x="{BAR_X[0]:g}" y="{c - BAR_HEIGHT / 2:g}" width="{BAR_X[1] - BAR_X[0]:g}" '
        f'height="{BAR_HEIGHT:g}" fill="{C["brass"]}"/>'
        for c in BAR_CENTRES
    )
    return (
        f'<g transform="translate({tx:g} {ty:g}) scale({scale:g})">'
        f'<rect x="{PLATE[0] + half:g}" y="{PLATE[1] + half:g}" '
        f'width="{PLATE[2] - PLATE[0] - BEVEL:g}" height="{PLATE[3] - PLATE[1] - BEVEL:g}" rx="2" '
        f'fill="{C["field-ink"]}" stroke="{C["steel-bevel"]}" stroke-width="{BEVEL:g}"/>'
        f"{bars}</g>"
    )


def avatar_svg() -> str:
    """Returns the avatar source SVG."""
    half = AVATAR / 2
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {AVATAR} {AVATAR}" '
        f'width="{AVATAR}" height="{AVATAR}" role="img" aria-label="CAPIE">\n'
        "  <!-- capie-mods avatar: the CAPIE connector mark on panel-umber. Tokens: capie-design "
        "tokens.json 1.2.0. Kept inside the circle GitHub crops avatars to. -->\n"
        f'  <rect width="{AVATAR}" height="{AVATAR}" fill="{C["panel-umber"]}"/>\n'
        f"  {mark_svg(AVATAR_SCALE, half, half)}\n"
        "</svg>\n"
    )


def avatar_png() -> bytes:
    """Draws the avatar PNG with 4x supersampling from the same geometry as the SVG."""
    ss = 4
    s = AVATAR_SCALE * ss
    tx = AVATAR * ss / 2 - MARK_CENTRE[0] * s
    ty = AVATAR * ss / 2 - MARK_CENTRE[1] * s

    def at(x: float, y: float) -> tuple[int, int]:
        return (round(tx + x * s), round(ty + y * s))

    img = Image.new("RGB", (AVATAR * ss, AVATAR * ss), C["panel-umber"])
    pen = ImageDraw.Draw(img)
    pen.rounded_rectangle(
        (*at(PLATE[0], PLATE[1]), *at(PLATE[2], PLATE[3])),
        radius=round(2 * s),
        fill=C["field-ink"],
        outline=C["steel-bevel"],
        width=round(BEVEL * s),
    )
    for c in BAR_CENTRES:
        pen.rectangle(
            (*at(BAR_X[0], c - BAR_HEIGHT / 2), *at(BAR_X[1], c + BAR_HEIGHT / 2)),
            fill=C["brass"],
        )
    img = img.resize((AVATAR, AVATAR), Image.Resampling.LANCZOS)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG", optimize=True)
    return buffer.getvalue()


FONT = "Ubuntu,'Segoe UI','DejaVu Sans',Verdana,sans-serif"
"""Design-system font stack; SVGs shown on GitHub cannot load web fonts."""


def banner_svg(*, dark: bool) -> str:
    """Returns the profile banner for one page scheme.

    The background is transparent so the banner sits on GitHub's own page colour. The mark
    keeps its panel-umber tile in both schemes, as diagrams keep their own canvas.

    Args:
        dark: True for the dark page scheme.

    Returns:
        The SVG document.
    """
    name = C["parchment"] if dark else C["light-fg"]
    sub = C["khaki"] if dark else C["light-fg-2"]
    tile = 128
    rim = "" if dark else f' stroke="{C["panel-rim"]}" stroke-width="1"'
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 160" width="880" height="160" '
        'role="img" aria-labelledby="t">\n'
        "  <title id=\"t\">CAPIE (Cyprian's API Extender) for Hearts of Iron IV</title>\n"
        f'  <rect x="0.5" y="16.5" width="{tile - 1}" height="{tile - 1}" rx="6" '
        f'fill="{C["panel-umber"]}"{rim}/>\n'
        f"  {mark_svg(tile / AVATAR * AVATAR_SCALE, tile / 2, 16 + tile / 2)}\n"
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
        ASSETS / "org-avatar.svg": avatar_svg().encode(),
        ASSETS / "org-avatar.png": avatar_png(),
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
    print(f"status.svg width: {status_svg()[1]} px")
    return 1 if stale else 0


if __name__ == "__main__":
    sys.exit(main())
