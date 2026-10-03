"""Render the shared social preview card.

Social scrapers need a real raster image, so this is rendered once and the PNG is
committed rather than built on every deploy. Keeping it out of the deploy build
means production never depends on system fonts being present. Re-run it only when
the branding or the headline counts change:

    python scripts/build_og_card.py

Pillow arrives with reportlab in requirements.txt; the DejaVu fonts come from the
host. Both are build-time only.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tracker_catalog import CONDITION_NAMES, TRACKERS  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "og-card.png"
SITE_HOST = "yourpetshealthlog.netlify.app"

WIDTH, HEIGHT = 1200, 630
BRAND = "#55756C"
CREAM = "#FFFDF9"
INK = "#354842"
MUTED = "#687772"
LINE = "#DDE6E2"
SOFT = "#F5F8F6"

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
BOLD = FONT_DIR / "DejaVuSans-Bold.ttf"
REGULAR = FONT_DIR / "DejaVuSans.ttf"


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    if not path.is_file():
        raise SystemExit(f"Missing font for the social card: {path}")
    return ImageFont.truetype(str(path), size)


def draw_paw(draw: ImageDraw.ImageDraw, x: int, y: int, size: int) -> None:
    """The site paw mark: a rounded brand tile with five cream pads."""
    scale = size / 64
    draw.rounded_rectangle([x, y, x + size, y + size], radius=int(19 * scale), fill=BRAND)

    def pad(cx: float, cy: float, rx: float, ry: float) -> None:
        draw.ellipse(
            [x + (cx - rx) * scale, y + (cy - ry) * scale,
             x + (cx + rx) * scale, y + (cy + ry) * scale],
            fill=CREAM,
        )

    pad(32, 42, 14.5, 11.5)
    pad(14.5, 27, 5.4, 6.6)
    pad(26, 19, 5.3, 6.8)
    pad(38, 19, 5.3, 6.8)
    pad(49.5, 27, 5.4, 6.6)


def draw_pill(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, text_font) -> int:
    pad_x, pad_y = 22, 14
    width = int(draw.textlength(text, font=text_font))
    height = text_font.size + pad_y * 2
    draw.rounded_rectangle(
        [x, y, x + width + pad_x * 2, y + height], radius=height // 2, fill=SOFT, outline=LINE, width=2
    )
    draw.text((x + pad_x, y + pad_y - 2), text, font=text_font, fill=INK)
    return x + width + pad_x * 2


def main() -> int:
    image = Image.new("RGB", (WIDTH, HEIGHT), CREAM)
    draw = ImageDraw.Draw(image)

    draw.rectangle([0, 0, WIDTH, 14], fill=BRAND)
    draw.rectangle([0, HEIGHT - 76, WIDTH, HEIGHT], fill=BRAND)

    draw_paw(draw, 80, 74, 92)
    draw.text((196, 100), "Your Pet's Health Log", font=font(BOLD, 34), fill=INK)

    title = font(BOLD, 68)
    draw.text((80, 214), "Free printable pet", font=title, fill=INK)
    draw.text((80, 292), "health trackers", font=title, fill=INK)

    body = font(REGULAR, 30)
    draw.text(
        (80, 392),
        f"{len(TRACKERS)} trackers across {len(CONDITION_NAMES)} health concerns,",
        font=body,
        fill=MUTED,
    )
    draw.text((80, 432), "for the days between veterinary visits.", font=body, fill=MUTED)

    pill = font(BOLD, 24)
    cursor = draw_pill(draw, 80, 492, "Download a PDF", pill)
    cursor = draw_pill(draw, cursor + 16, 492, "Or fill it in online", pill)
    draw_pill(draw, cursor + 16, 492, "No account. No email.", pill)

    draw.text((80, HEIGHT - 54), SITE_HOST, font=font(BOLD, 28), fill=CREAM)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT, "PNG", optimize=True)
    print(f"Built {OUTPUT} ({OUTPUT.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
