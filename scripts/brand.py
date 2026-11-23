"""Make the trakit logo, icon, and social preview card.

Run from the repository root (Python 3.11 or later, for tomllib):

    uv run --no-project --with fonttools --with resvg-py python scripts/brand.py

It writes these files to docs/images/:

- logo-light.svg, logo-dark.svg, logo-light.png, logo-dark.png: the README header (GitHub light and dark mode)
- icon.svg, icon-32.png ... icon-512.png: favicon and avatar
- social.png: the GitHub social preview. Upload it by hand: Settings, General, Social preview.

The tagline below the word mark is the `description` in pyproject.toml. The README `alt` text has the same
sentence. Change both together.

The icon is three track rows. The middle row ends in a tag: trakit identifies a track from its title.
Palette: cream bars and an amber tag on a blue-black tile with a gray border.

All text is drawn as paths from scripts/brand/Nunito.ttf (SIL Open Font License, see scripts/brand/OFL.txt).
So the output does not depend on the fonts of the computer.

The trakit name, logo, and icon are not covered by the MIT license of this repository.
"""

import tomllib
from pathlib import Path

import resvg_py
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'docs' / 'images'
FONT = ROOT / 'scripts' / 'brand' / 'Nunito.ttf'
TAGLINE = tomllib.loads((ROOT / 'pyproject.toml').read_text(encoding='utf-8'))['project']['description']

TILE, BORDER, BARS, TAG = '#161b22', '#3d444d', '#f5efe0', '#b07d2a'
IT = '#b07d2a'  # contrast 3.6 on GitHub light, 5.2 on GitHub dark
LIGHT, DARK = '#1f2328', '#f0f6fc'  # GitHub text colors
GITHUB_DARK = '#0d1117'


def font(weight: int) -> TTFont:
    f = TTFont(FONT)
    return instantiateVariableFont(f, {a.axisTag: weight if a.axisTag == 'wght' else None for a in f['fvar'].axes})


def text_path(f: TTFont, text: str, height: float, ref: str) -> tuple[str, float]:
    """Return (d, width): text as SVG path data, from x=0.

    The glyph box of `ref` is `height` high, and its top is at y=0.
    """
    glyphs, cmap = f.getGlyphSet(), f.getBestCmap()
    bounds, x = BoundsPen(glyphs), 0.0
    for ch in ref:
        glyphs[cmap[ord(ch)]].draw(TransformPen(bounds, (1, 0, 0, 1, x, 0)))
        x += glyphs[cmap[ord(ch)]].width
    assert bounds.bounds is not None
    _, y_min, _, y_max = bounds.bounds
    scale = height / (y_max - y_min)
    pen, x = SVGPathPen(glyphs), 0.0
    for ch in text:
        glyph = glyphs[cmap[ord(ch)]]
        glyph.draw(TransformPen(pen, (scale, 0, 0, -scale, x, y_max * scale)))
        x += glyph.width * scale
    return pen.getCommands(), x


def tag(x: float, y: float, w: float, h: float) -> str:
    """Draw a label tag: a point at the left, round corners at the right, a hole near the point."""
    n, r, hr = h * 0.45, h * 0.18, h * 0.12
    cx, cy = x + n * 0.95, y + h / 2
    body = (
        f'M{x:.2f} {cy:.2f} L{x + n:.2f} {y:.2f} H{x + w - r:.2f} A{r:.2f} {r:.2f} 0 0 1 {x + w:.2f} {y + r:.2f} '
        f'V{y + h - r:.2f} A{r:.2f} {r:.2f} 0 0 1 {x + w - r:.2f} {y + h:.2f} H{x + n:.2f} Z'
    )
    hole = f'M{cx - hr:.2f} {cy:.2f} a{hr:.2f} {hr:.2f} 0 1 0 {2 * hr:.2f} 0 a{hr:.2f} {hr:.2f} 0 1 0 {-2 * hr:.2f} 0 Z'
    return f'<path d="{body} {hole}" fill="{TAG}" fill-rule="evenodd"/>'


def rows() -> str:
    """Draw three bars from x=20 to x=80. The middle bar is short, and a tag ends that row."""
    bar, gap = 13, 3
    th = bar * 1.5
    tw = th * 1.9
    out = tag(80 - tw, 50 - th / 2, tw, th)
    for cy in (29, 50, 71):
        w = 80 - tw - gap - 20 if cy == 50 else 60
        out += f'<rect x="20" y="{cy - bar / 2}" width="{w:.2f}" height="{bar}" rx="{bar / 2}" fill="{BARS}"/>'
    return out


def icon() -> str:
    """Draw a dark tile with a thin gray border (visible on GitHub dark), and the track rows."""
    return (
        f'<rect x="1" y="1" width="98" height="98" rx="21" fill="{TILE}"/>{rows()}'
        f'<rect x="1" y="1" width="98" height="98" rx="21" fill="none" stroke="{BORDER}" stroke-width="2"/>'
    )


def logo(color: str, trak: tuple[str, float], it: tuple[str, float], tagline: tuple[str, float]) -> tuple[str, float]:
    """Return (SVG body, width): the icon, then the word mark ("it" in amber) with the tagline below it.

    The height is 100.
    """
    body = (
        f'<svg width="100" height="100" viewBox="0 0 100 100">{icon()}</svg>'
        f'<path transform="translate(124 0)" d="{trak[0]}" fill="{color}"/>'
        f'<path transform="translate({124 + trak[1]:.2f} 0)" d="{it[0]}" fill="{IT}"/>'
        f'<path transform="translate(124 74)" d="{tagline[0]}" fill="{color}" fill-opacity=".75"/>'
    )
    return body, 124 + max(trak[1] + it[1], tagline[1]) + 4  # 4: margin, the 't' goes past its advance


def svg(body: str, w: float, h: float) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.1f} {h:.1f}" width="{w:.0f}" height="{h:.0f}">'
        f'{body}</svg>'
    )


def png(name: str, content: str, w: float, h: float) -> None:
    data = resvg_py.svg_to_bytes(svg_string=content, width=round(w), height=round(h), skip_system_fonts=True)
    (OUT / name).write_bytes(bytes(data))


def main() -> None:
    heavy = font(1000)
    trak = text_path(heavy, 'trak', 62, 'trakit')
    it = text_path(heavy, 'it', 62, 'trakit')
    tagline = text_path(font(600), TAGLINE, 24, TAGLINE)

    for name, color in (('logo-light', LIGHT), ('logo-dark', DARK)):
        body, w = logo(color, trak, it, tagline)
        (OUT / f'{name}.svg').write_text(svg(body, w, 100) + '\n', encoding='utf-8')
        png(f'{name}.png', svg(body, w, 100), w * 4, 400)

    (OUT / 'icon.svg').write_text(svg(icon(), 100, 100) + '\n', encoding='utf-8')
    for size in (32, 64, 256, 512):
        png(f'icon-{size}.png', svg(icon(), 100, 100), size, size)

    body, w = logo(DARK, trak, it, tagline)
    scale = min(2.6, 1080 / w)  # 100 px margin at the left and the right
    card = (
        f'<rect width="1280" height="640" fill="{GITHUB_DARK}"/>'
        f'<g transform="translate({(1280 - w * scale) / 2:.1f} {320 - 50 * scale:.1f}) scale({scale})">{body}</g>'
    )
    png('social.png', svg(card, 1280, 640), 1280, 640)


if __name__ == '__main__':
    main()
