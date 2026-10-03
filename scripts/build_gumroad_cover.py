"""Generate a simple Gumroad cover image for the household binder."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "fulfillment" / "household-binder" / "gumroad-cover.png"


def font(size: int):
    for name in ("arial.ttf", "segoeui.ttf", "C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/segoeui.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def main() -> int:
    width, height = 1200, 1200
    img = Image.new("RGB", (width, height), "#FFFDF9")
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, width, 280], fill="#55756C")
    draw.text((72, 90), "Your Pet's Health Log", fill="white", font=font(36))
    draw.text((72, 155), "Household Pet Care Binder", fill="white", font=font(58))
    draw.text((72, 360), "& Sitter Handover", fill="#354842", font=font(52))
    lines = [
        "29 fillable pages",
        "US Letter + A4 included",
        "Profile, vaccines, meds, vet log",
        "Emergency contacts + sitter handbook",
        "Not a reprint of the free trackers",
    ]
    y = 520
    for line in lines:
        draw.ellipse([72, y + 8, 92, y + 28], fill="#55756C")
        draw.text((110, y), line, fill="#354842", font=font(30))
        y += 70
    draw.text((72, 1080), "$12  ·  Instant download", fill="#687772", font=font(34))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, "PNG")
    print(f"Wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
