"""Generate every Steady Paws printable tracker from the shared catalog."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

from tracker_catalog import TRACKERS

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "downloads"
OUT.mkdir(parents=True, exist_ok=True)

BRAND = HexColor("#163A33")
BRAND2 = HexColor("#255C50")
CREAM = HexColor("#FBFAF6")
INK = HexColor("#18312C")
MUTED = HexColor("#5F706B")
LINE = HexColor("#D7E1DC")
SOFT = HexColor("#F6F8F7")
WARN = HexColor("#FFF5DF")
WARN_INK = HexColor("#5B513C")


def wrap_text(text: str, font: str, size: float, max_width: float) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if stringWidth(candidate, font, size) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_header(c: canvas.Canvas, spec: dict, page: int, subtitle: str | None = None) -> None:
    width, height = letter
    c.setFillColor(CREAM)
    c.rect(0, 0, width, height, stroke=0, fill=1)
    c.setFillColor(BRAND)
    c.rect(0, height - 88, width, 88, stroke=0, fill=1)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(36, height - 30, "STEADY PAWS")
    c.setFillColor(HexColor("#D7E9E2"))
    c.setFont("Helvetica-Bold", 8)
    c.drawRightString(width - 36, height - 30, spec["species"].upper())
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(36, height - 56, spec["title"])
    c.setFillColor(HexColor("#D7E9E2"))
    c.setFont("Helvetica", 8.3)
    c.drawString(36, height - 73, subtitle or spec["subtitle"])
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 7.5)
    c.drawRightString(width - 36, 20, f"Page {page} | steadypaws.netlify.app")


def draw_disclaimer(c: canvas.Canvas) -> None:
    width, _ = letter
    y = 45
    c.setFillColor(WARN)
    c.roundRect(36, y, width - 72, 35, 6, stroke=0, fill=1)
    c.setFillColor(WARN_INK)
    c.setFont("Helvetica", 6.8)
    text = (
        "Care organizer only - not diagnosis or treatment. Record only measurements, medicines, and care targets "
        "their veterinary team asks you to use. Contact a veterinarian for concerning or urgent changes."
    )
    for index, line in enumerate(wrap_text(text, "Helvetica", 6.8, width - 94)[:2]):
        c.drawString(47, y + 22 - index * 10, line)


def draw_identity(c: canvas.Canvas) -> None:
    _, height = letter
    y = height - 116
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 8)
    entries = (("Their name", 36, 174), ("Week of", 220, 130), ("Their veterinarian", 360, 216))
    for label, x, width in entries:
        c.drawString(x, y, label)
        c.setStrokeColor(LINE)
        c.line(x, y - 13, x + width, y - 13)


def draw_daily_table(c: canvas.Canvas, fields: list[str]) -> None:
    width, height = letter
    x0, y_top, table_width, row_height = 36, height - 158, width - 72, 42
    weights = [0.95] + [1] * (len(fields) - 2) + [1.5]
    total = sum(weights)
    widths = [table_width * weight / total for weight in weights]

    c.setFillColor(BRAND)
    c.roundRect(x0, y_top - 24, table_width, 24, 5, stroke=0, fill=1)
    x = x0
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 6.7)
    for field, col_width in zip(fields, widths):
        lines = wrap_text(field, "Helvetica-Bold", 6.7, col_width - 6)
        c.drawCentredString(x + col_width / 2, y_top - 10, lines[0])
        if len(lines) > 1:
            c.drawCentredString(x + col_width / 2, y_top - 19, lines[1])
        x += col_width

    c.setStrokeColor(LINE)
    c.setLineWidth(0.6)
    y = y_top - 24
    for row in range(11):
        y2 = y - row_height
        c.setFillColor(white if row % 2 == 0 else SOFT)
        c.rect(x0, y2, table_width, row_height, stroke=0, fill=1)
        c.setStrokeColor(LINE)
        c.line(x0, y2, x0 + table_width, y2)
        x = x0
        for col_width in widths[:-1]:
            x += col_width
            c.line(x, y2, x, y2 + row_height)
        y = y2
    c.rect(x0, y_top - 24 - row_height * 11, table_width, row_height * 11 + 24, stroke=1, fill=0)


def draw_summary(c: canvas.Canvas, items: list[str]) -> None:
    width, height = letter
    x0, y = 36, height - 135
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(x0, y, "How they did this week")
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8.5)
    c.drawString(x0, y - 18, "Use the little patterns you noticed to make their next veterinary conversation easier.")
    y -= 52

    for index, item in enumerate(items):
        col, row = index % 2, index // 2
        x, yy = x0 + col * 270, y - row * 58
        c.setStrokeColor(BRAND2)
        c.setLineWidth(1)
        c.roundRect(x, yy - 11, 12, 12, 2, stroke=1, fill=0)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 8)
        label = wrap_text(item, "Helvetica-Bold", 8, 222)[0]
        c.drawString(x + 20, yy - 3, label)
        c.setStrokeColor(LINE)
        c.line(x + 20, yy - 17, x + 245, yy - 17)
        c.line(x + 20, yy - 30, x + 245, yy - 30)

    y2 = y - 4 * 58 - 18
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x0, y2, "What changed since their last visit")
    c.setStrokeColor(LINE)
    for i in range(3):
        c.line(x0, y2 - 18 - i * 22, width - 36, y2 - 18 - i * 22)

    y3 = y2 - 92
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x0, y3, "Questions for their veterinary team")
    for i in range(4):
        c.line(x0, y3 - 18 - i * 22, width - 36, y3 - 18 - i * 22)

    y4 = y3 - 118
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x0, y4, "Their veterinary plan / next steps")
    for i in range(3):
        c.line(x0, y4 - 18 - i * 22, width - 36, y4 - 18 - i * 22)


def make_pdf(spec: dict) -> Path:
    path = OUT / spec["filename"]
    c = canvas.Canvas(str(path), pagesize=letter, pageCompression=1)
    c.setTitle(spec["title"])
    c.setAuthor("Steady Paws")
    c.setSubject(f"Printable {spec['species']} care tracker for veterinary conversations")

    draw_header(c, spec, 1)
    draw_identity(c)
    draw_daily_table(c, spec["fields"])
    draw_disclaimer(c)
    c.showPage()

    draw_header(c, spec, 2, "How they did this week + veterinary visit notes")
    draw_summary(c, spec["summary"])
    draw_disclaimer(c)
    c.save()
    return path


def main() -> int:
    for spec in TRACKERS:
        print(make_pdf(spec))
    print(f"COUNT {len(TRACKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
