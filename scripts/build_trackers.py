"""Generate every Steady Paws printable care form from the shared catalog."""

from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.generic import BooleanObject, DictionaryObject, NameObject, TextStringObject
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

from tracker_catalog import TRACKERS, condition_name

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "downloads"
OUT.mkdir(parents=True, exist_ok=True)

BRAND = HexColor("#55756C")
BRAND2 = HexColor("#5F776F")
CREAM = HexColor("#FFFDF9")
INK = HexColor("#354842")
MUTED = HexColor("#687772")
LINE = HexColor("#DDE6E2")
SOFT = HexColor("#F5F8F6")
PHOTO_SOFT = HexColor("#FBF2ED")
PHOTO_INK = HexColor("#7B695F")
WARN = HexColor("#FBF3E9")
WARN_INK = HexColor("#746457")
HEADER_LIGHT = HexColor("#EDF6F3")
IDENTITY_BG = HexColor("#FFFEFA")

GROUP_ACCENTS = {
    "cat": HexColor("#EBCFC6"),
    "dog": HexColor("#CFE0D9"),
    "small-mammal": HexColor("#E2D8EA"),
    "bird": HexColor("#D7E8EB"),
    "reptile": HexColor("#DDE7CF"),
    "horse": HexColor("#E8D6C2"),
    "aquatic": HexColor("#CFE7E5"),
    "universal": HexColor("#E9DFC5"),
}

# These coordinates are also used by browser personalization code.
# Keep them stable or update every personalization path at the same time.
PHOTO_BOX = (486, 603, 90, 90)
PHOTO_IMAGE_BOX = (490, 607, 82, 82)
NAME_TEXT_POSITION = (96, 666)


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


def form_title(spec: dict) -> str:
    concern = condition_name(spec)
    if spec["group"] == "universal":
        return concern
    return f"{concern} Care Log"


def accent_for(spec: dict):
    return GROUP_ACCENTS.get(spec.get("group"), GROUP_ACCENTS["universal"])


def display_field(field: str) -> str:
    """Make catalog labels calmer and easier to scan on a printed form."""
    cleaned = field.replace("*", "").strip()
    lowered = cleaned.lower().replace(" ", "")
    if lowered in {"time", "date/time", "datetime"}:
        return "Date / time"
    replacements = {
        "Medication": "Medicine",
        "Medication given": "Medicine",
        "Insulin given": "Insulin",
        "Medication/fluids": "Medicine / fluids",
        "Food/appetite": "Food / appetite",
    }
    return replacements.get(cleaned, cleaned)


def draw_paw_mark(c: canvas.Canvas, x: float, y: float, scale: float = 1.0, color=white) -> None:
    c.saveState()
    c.setFillColor(color)
    c.ellipse(x + 6 * scale, y, x + 20 * scale, y + 12 * scale, stroke=0, fill=1)
    c.ellipse(x, y + 12 * scale, x + 7 * scale, y + 21 * scale, stroke=0, fill=1)
    c.ellipse(x + 7 * scale, y + 18 * scale, x + 14 * scale, y + 27 * scale, stroke=0, fill=1)
    c.ellipse(x + 16 * scale, y + 18 * scale, x + 23 * scale, y + 27 * scale, stroke=0, fill=1)
    c.ellipse(x + 23 * scale, y + 11 * scale, x + 30 * scale, y + 20 * scale, stroke=0, fill=1)
    c.restoreState()


def draw_fitted_title(c: canvas.Canvas, text: str, x: float, y: float, max_width: float) -> None:
    size = 20.0
    while size > 13 and stringWidth(text, "Helvetica-Bold", size) > max_width:
        size -= 0.5
    c.setFont("Helvetica-Bold", size)
    c.drawString(x, y, text)


def draw_header(c: canvas.Canvas, spec: dict, page: int, subtitle: str | None = None) -> None:
    width, height = letter
    accent = accent_for(spec)
    c.setFillColor(CREAM)
    c.rect(0, 0, width, height, stroke=0, fill=1)
    c.setFillColor(BRAND)
    c.rect(0, height - 88, width, 88, stroke=0, fill=1)
    c.setFillColor(accent)
    c.rect(0, height - 92, width, 4, stroke=0, fill=1)

    draw_paw_mark(c, 36, height - 44, scale=0.58, color=white)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(58, height - 30, "STEADY PAWS")

    species = spec["species"].upper()
    badge_width = max(70, min(145, stringWidth(species, "Helvetica-Bold", 7.5) + 20))
    c.setFillColor(accent)
    c.roundRect(width - 36 - badge_width, height - 41, badge_width, 20, 10, stroke=0, fill=1)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawCentredString(width - 36 - badge_width / 2, height - 34, species)

    c.setFillColor(white)
    draw_fitted_title(c, form_title(spec), 36, height - 58, width - 72)
    c.setFillColor(HEADER_LIGHT)
    c.setFont("Helvetica", 8.3)
    c.drawString(36, height - 75, subtitle or spec["subtitle"])
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 7.5)
    c.drawRightString(width - 36, 20, f"Page {page} | steadypaws.netlify.app")


def draw_disclaimer(c: canvas.Canvas) -> None:
    width, _ = letter
    y = 45
    c.setFillColor(WARN)
    c.setStrokeColor(HexColor("#E7D6C7"))
    c.roundRect(36, y, width - 72, 35, 6, stroke=1, fill=1)
    c.setFillColor(WARN_INK)
    c.setFont("Helvetica", 7)
    text = (
        "For organizing care, not medical advice. Follow their veterinarian's plan and contact a veterinarian "
        "for urgent or concerning changes."
    )
    for index, line in enumerate(wrap_text(text, "Helvetica", 7, width - 94)[:2]):
        c.drawString(47, y + 22 - index * 10, line)


def draw_photo_placeholder(c: canvas.Canvas, accent) -> None:
    x, y, box_w, box_h = PHOTO_BOX
    c.setFillColor(PHOTO_SOFT)
    c.setStrokeColor(HexColor("#9D897A"))
    c.setLineWidth(0.8)
    c.roundRect(x, y, box_w, box_h, 14, stroke=1, fill=1)
    draw_paw_mark(c, x + 31, y + 50, scale=0.85, color=accent)
    c.setFillColor(PHOTO_INK)
    c.setFont("Helvetica-Bold", 7.2)
    c.drawCentredString(x + box_w / 2, y + 34, "THEIR PHOTO")
    c.setFont("Helvetica", 6.6)
    c.drawCentredString(x + box_w / 2, y + 22, "optional")


def draw_identity(c: canvas.Canvas, spec: dict) -> None:
    width, height = letter
    accent = accent_for(spec)

    c.setFillColor(IDENTITY_BG)
    c.setStrokeColor(accent)
    c.setLineWidth(1.0)
    c.roundRect(28, 558, width - 56, 150, 14, stroke=1, fill=1)
    c.setFillColor(accent)
    c.roundRect(36, 688, 70, 15, 7.5, stroke=0, fill=1)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 6.8)
    c.drawString(48, 693, "CARE DETAILS")

    # Name baseline stays aligned with browser PDF personalization coordinates.
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 8)
    name_y = height - 116
    c.drawString(36, name_y, "Their name")
    c.setStrokeColor(LINE)
    c.line(94, name_y - 13, 290, name_y - 13)

    c.setFillColor(INK)
    c.drawString(306, name_y, "Week of")
    c.setStrokeColor(LINE)
    c.line(348, name_y - 13, 466, name_y - 13)

    vet_y = height - 150
    c.setFillColor(INK)
    c.drawString(36, vet_y, "Veterinarian")
    c.setStrokeColor(LINE)
    c.line(96, vet_y - 13, 466, vet_y - 13)

    primary_y = height - 183
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 7.7)
    c.drawString(36, primary_y, "Main health concern")
    c.setFont("Helvetica", 8)
    c.drawString(135, primary_y, condition_name(spec))
    c.setStrokeColor(LINE)
    c.line(135, primary_y - 13, 466, primary_y - 13)

    other_y = height - 214
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 7.7)
    c.drawString(36, other_y, "Other health conditions")
    c.setStrokeColor(LINE)
    c.line(143, other_y - 13, 466, other_y - 13)

    draw_photo_placeholder(c, accent)


def draw_daily_table(c: canvas.Canvas, spec: dict) -> None:
    width, height = letter
    fields = [display_field(field) for field in spec["fields"]]
    x0, y_top, table_width, row_height = 36, height - 266, width - 72, 34
    weights = [1.1] + [1] * (len(fields) - 2) + [1.5]
    total = sum(weights)
    widths = [table_width * weight / total for weight in weights]

    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x0, y_top + 14, "Daily care log")
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 7.2)
    c.drawString(x0 + 80, y_top + 14, "Use one row each time you check or give care.")

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


def draw_summary_prompt(c: canvas.Canvas, label: str, x: float, y: float, fill) -> None:
    c.setFillColor(fill)
    c.setStrokeColor(LINE)
    c.roundRect(x - 6, y - 36, 258, 43, 8, stroke=1, fill=1)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 7.8)
    lines = wrap_text(display_field(label), "Helvetica-Bold", 7.8, 225)[:2]
    for index, line in enumerate(lines):
        c.drawString(x, y - 3 - index * 10, line)
    writing_top = y - 16 if len(lines) == 1 else y - 23
    c.setStrokeColor(LINE)
    c.line(x, writing_top, x + 244, writing_top)
    c.line(x, y - 31, x + 244, y - 31)


def draw_summary(c: canvas.Canvas, spec: dict) -> None:
    width, height = letter
    items = spec["summary"]
    accent = accent_for(spec)
    x0, y = 36, height - 138

    c.setFillColor(accent)
    c.roundRect(x0, y - 9, 170, 30, 15, stroke=0, fill=1)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(x0 + 14, y, "This week at a glance")
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8.3)
    c.drawString(x0, y - 25, "Note the changes or patterns that matter most. Bring this page to the next visit.")
    y -= 48

    for index, item in enumerate(items):
        col, row = index % 2, index // 2
        x, yy = x0 + col * 270, y - row * 54
        draw_summary_prompt(c, item, x, yy, SOFT if row % 2 == 0 else IDENTITY_BG)

    y2 = y - 4 * 54 - 18
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x0, y2, "Since the last vet visit")
    c.setStrokeColor(LINE)
    for i in range(3):
        c.line(x0, y2 - 18 - i * 22, width - 36, y2 - 18 - i * 22)

    y3 = y2 - 88
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x0, y3, "Questions for the vet")
    for i in range(3):
        c.line(x0, y3 - 18 - i * 22, width - 36, y3 - 18 - i * 22)

    y4 = y3 - 94
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x0, y4, "Plan / next steps from the vet")
    for i in range(3):
        c.line(x0, y4 - 18 - i * 22, width - 36, y4 - 18 - i * 22)


def enhance_pdf(path: Path, spec: dict) -> None:
    """Add language, display-title metadata, and simple page bookmarks."""
    reader = PdfReader(str(path))
    writer = PdfWriter()
    writer.append_pages_from_reader(reader)
    writer.add_metadata(
        {
            "/Title": form_title(spec),
            "/Author": "Steady Paws",
            "/Subject": f"Printable {condition_name(spec)} care paperwork for {spec['species'].lower()} veterinary conversations",
        }
    )
    writer._root_object.update(
        {
            NameObject("/Lang"): TextStringObject("en-US"),
            NameObject("/PageMode"): NameObject("/UseOutlines"),
            NameObject("/ViewerPreferences"): DictionaryObject(
                {NameObject("/DisplayDocTitle"): BooleanObject(True)}
            ),
        }
    )
    writer.add_outline_item("Daily care log", 0)
    writer.add_outline_item("Weekly notes and vet visit prep", 1)
    temp = path.with_suffix(".tmp.pdf")
    with temp.open("wb") as handle:
        writer.write(handle)
    temp.replace(path)


def make_pdf(spec: dict) -> Path:
    path = OUT / spec["filename"]
    c = canvas.Canvas(str(path), pagesize=letter, pageCompression=1)
    c.setTitle(form_title(spec))
    c.setAuthor("Steady Paws")
    c.setSubject(f"Printable {condition_name(spec)} care paperwork for {spec['species'].lower()} veterinary conversations")

    draw_header(c, spec, 1)
    draw_identity(c, spec)
    draw_daily_table(c, spec)
    draw_disclaimer(c)
    c.showPage()

    draw_header(c, spec, 2, "Weekly notes + vet visit prep")
    draw_summary(c, spec)
    draw_disclaimer(c)
    c.save()
    enhance_pdf(path, spec)
    return path


def main() -> int:
    for spec in TRACKERS:
        print(make_pdf(spec))
    print(f"COUNT {len(TRACKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
