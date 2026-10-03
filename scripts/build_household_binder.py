"""Build the paid Household Pet Care Binder & Sitter Handover (US Letter + A4).

This is the ONE Gumroad product. It is not a reprint of the free 72 condition trackers.
"""

from __future__ import annotations

import json
import logging
import zipfile
from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4, letter
from reportlab.pdfgen import canvas

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
LOGGER = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "fulfillment" / "household-binder"
META_PATH = ROOT / "data" / "household_binder.json"
SITE = "yourpetshealthlog.netlify.app"

BRAND = HexColor("#55756C")
INK = HexColor("#354842")
MUTED = HexColor("#687772")
LINE = HexColor("#DDE6E2")
CREAM = HexColor("#FFFDF9")
SOFT = HexColor("#F5F8F6")


class BinderCanvas:
    def __init__(self, path: Path, pagesize):
        self.path = path
        self.pagesize = pagesize
        self.width, self.height = pagesize
        self.c = canvas.Canvas(str(path), pagesize=pagesize)
        self.c.setTitle("Household Pet Care Binder & Sitter Handover")
        self.c.setAuthor("Your Pet’s Health Log")
        self._field = 0
        self.page_no = 0

    def _fid(self, prefix: str) -> str:
        self._field += 1
        return f"{prefix}_{self._field}"

    def new_page(self, title: str, subtitle: str = "") -> None:
        if self.page_no:
            self.c.showPage()
        self.page_no += 1
        self.c.setFillColor(CREAM)
        self.c.rect(0, 0, self.width, self.height, fill=1, stroke=0)
        self.c.setFillColor(BRAND)
        self.c.rect(0, self.height - 48, self.width, 48, fill=1, stroke=0)
        self.c.setFillColor(white)
        self.c.setFont("Helvetica-Bold", 11)
        self.c.drawString(36, self.height - 30, "Your Pet’s Health Log")
        self.c.setFont("Helvetica", 8)
        self.c.drawRightString(self.width - 36, self.height - 30, f"Page {self.page_no}")
        self.c.setFillColor(INK)
        self.c.setFont("Helvetica-Bold", 16)
        self.c.drawString(36, self.height - 78, title)
        y = self.height - 96
        if subtitle:
            self.c.setFillColor(MUTED)
            self.c.setFont("Helvetica", 9)
            self.c.drawString(36, y, subtitle)
            y -= 16
        self.y = y - 8

    def footer(self, note: str = "") -> None:
        self.c.setStrokeColor(LINE)
        self.c.line(36, 42, self.width - 36, 42)
        self.c.setFillColor(MUTED)
        self.c.setFont("Helvetica", 7)
        self.c.drawString(36, 28, note or "Organizational aid only — not veterinary advice.")
        self.c.drawRightString(self.width - 36, 28, SITE)

    def label(self, text: str, x: float | None = None, y: float | None = None) -> None:
        self.c.setFillColor(MUTED)
        self.c.setFont("Helvetica-Bold", 8)
        self.c.drawString(x if x is not None else 36, y if y is not None else self.y, text)
        if y is None:
            self.y -= 12

    def field(self, w: float, h: float = 16, x: float | None = None, y: float | None = None, multiline: bool = False) -> None:
        fx = x if x is not None else 36
        fy = y if y is not None else self.y - h
        name = self._fid("f")
        form = self.c.acroForm
        if multiline:
            form.textfield(
                name=name, x=fx, y=fy, width=w, height=h,
                borderWidth=0.6, borderColor=LINE, fillColor=white,
                textColor=INK, forceBorder=True, fontSize=9, fieldFlags="multiline",
            )
        else:
            form.textfield(
                name=name, x=fx, y=fy, width=w, height=h,
                borderWidth=0.6, borderColor=LINE, fillColor=white,
                textColor=INK, forceBorder=True, fontSize=9,
            )
        if y is None:
            self.y = fy - 10

    def labeled_field(self, label: str, w: float, h: float = 16) -> None:
        self.label(label)
        self.field(w, h)

    def row_fields(self, items: list[tuple[str, float]], h: float = 16, gap: float = 10) -> None:
        x = 36
        label_y = self.y
        field_y = self.y - 12 - h
        for label, w in items:
            self.label(label, x=x, y=label_y)
            self.field(w, h, x=x, y=field_y)
            x += w + gap
        self.y = field_y - 12

    def section(self, title: str) -> None:
        self.y -= 4
        self.c.setFillColor(SOFT)
        self.c.roundRect(36, self.y - 18, self.width - 72, 22, 4, fill=1, stroke=0)
        self.c.setFillColor(BRAND)
        self.c.setFont("Helvetica-Bold", 9)
        self.c.drawString(44, self.y - 12, title)
        self.y -= 34

    def bullets(self, lines: list[str]) -> None:
        self.c.setFillColor(INK)
        self.c.setFont("Helvetica", 9)
        for line in lines:
            self.c.drawString(40, self.y, f"• {line}")
            self.y -= 13

    def checkbox_row(self, labels: list[str]) -> None:
        x = 36
        for label in labels:
            name = self._fid("c")
            self.c.acroForm.checkbox(
                name=name, x=x, y=self.y - 10, size=10,
                borderWidth=0.6, borderColor=LINE, fillColor=white, checked=False,
            )
            self.c.setFillColor(INK)
            self.c.setFont("Helvetica", 8)
            self.c.drawString(x + 14, self.y - 8, label)
            x += 110
        self.y -= 22

    def save(self) -> None:
        self.c.save()


def build_pages(doc: BinderCanvas) -> None:
    # 1 Cover
    doc.c.setFillColor(CREAM)
    doc.c.rect(0, 0, doc.width, doc.height, fill=1, stroke=0)
    doc.c.setFillColor(BRAND)
    doc.c.rect(0, doc.height - 160, doc.width, 160, fill=1, stroke=0)
    doc.c.setFillColor(white)
    doc.c.setFont("Helvetica-Bold", 12)
    doc.c.drawString(40, doc.height - 50, "Your Pet’s Health Log")
    doc.c.setFont("Helvetica-Bold", 26)
    doc.c.drawString(40, doc.height - 100, "Household Pet Care Binder")
    doc.c.setFont("Helvetica", 14)
    doc.c.drawString(40, doc.height - 126, "& Sitter Handover")
    doc.c.setFillColor(INK)
    doc.c.setFont("Helvetica", 11)
    y = doc.height - 210
    for line in (
        "Fillable printable binder for the household paperwork the free site does not include.",
        "Pet profile · vaccines · meds · vet log · emergency contacts · sitter handbook · travel.",
        "Use one copy per pet. Pair with free condition trackers at yourpetshealthlog.netlify.app.",
    ):
        doc.c.drawString(40, y, line)
        y -= 18
    doc.c.setFillColor(MUTED)
    doc.c.setFont("Helvetica", 9)
    doc.c.drawString(40, 60, "Organizational aid only — not a diagnosis or treatment plan.")
    doc.c.drawString(40, 44, "US Letter and A4 editions included with your purchase.")
    doc.page_no = 1

    # 2 How to use
    doc.new_page("How to use this binder", "Keep free condition trackers on the website. Use this binder for household records and sitters.")
    doc.bullets([
        "Make one copy of the profile and health pages for each pet in the home.",
        "Type into the fillable fields, or print blank and write by hand.",
        "Give the sitter handbook section to anyone watching your pets.",
        "Bring the vet visit log and medication pages to appointments.",
        "Free sick-day / condition trackers stay free on Your Pet’s Health Log.",
    ])
    doc.y -= 8
    doc.section("What’s inside")
    doc.bullets([
        "Pet profile with microchip, insurance, and veterinary contacts",
        "Vaccines & preventatives, medication schedule, vet visit log",
        "Emergency contacts and authorization notes",
        "Sitter handbook: routine, behavior, house rules, handover checklist",
        "Feeding, supplies, grooming, weight, expenses, travel go-bag",
    ])
    doc.footer()

    # 3-4 Pet profile
    doc.new_page("Pet profile", "Identity and everyday details")
    doc.row_fields([("Pet name", 220), ("Species / breed", 220)])
    doc.row_fields([("Date of birth / age", 160), ("Sex", 100), ("Color / markings", 180)])
    doc.row_fields([("Weight", 100), ("Microchip number", 220), ("License / ID tag", 160)])
    doc.labeled_field("Personality / quirks", doc.width - 72, 48)
    doc.labeled_field("Allergies / known reactions", doc.width - 72, 36)
    doc.labeled_field("Current health conditions (summary)", doc.width - 72, 48)
    doc.footer("Copy this page for each pet.")

    doc.new_page("Care team & insurance", "Who to call and how they are covered")
    doc.section("Primary veterinarian")
    doc.row_fields([("Clinic name", 220), ("Phone", 160)])
    doc.labeled_field("Address", doc.width - 72)
    doc.row_fields([("Preferred doctor", 220), ("After-hours / ER clinic", 220)])
    doc.section("Insurance & ID")
    doc.row_fields([("Insurance provider", 220), ("Policy number", 220)])
    doc.labeled_field("Claims phone / portal notes", doc.width - 72, 36)
    doc.labeled_field("Other specialists (dentist, cardio, behavior, etc.)", doc.width - 72, 48)
    doc.footer()

    # 5 Emergency
    doc.new_page("Emergency contacts", "Keep this page where a sitter can find it fast")
    for who in ("Owner / primary guardian", "Backup guardian", "Neighbor / local helper"):
        doc.section(who)
        doc.row_fields([("Name", 200), ("Phone", 160), ("Relationship", 120)])
    doc.labeled_field("Poison control / emergency notes", doc.width - 72, 48)
    doc.footer()

    # 6-7 Vaccines
    doc.new_page("Vaccines & preventatives", "Record what was given and when it is due again")
    doc.section("Vaccination log")
    for _ in range(8):
        doc.row_fields([("Vaccine", 150), ("Date given", 90), ("Next due", 90), ("Given by", 120)], h=14)
    doc.footer()

    doc.new_page("Preventatives schedule", "Flea, tick, heartworm, deworming, and other preventatives")
    for _ in range(8):
        doc.row_fields([("Product", 150), ("Dose / route", 100), ("Last given", 90), ("Next due", 100)], h=14)
    doc.labeled_field("Notes for the veterinary team", doc.width - 72, 60)
    doc.footer()

    # 8-9 Meds
    doc.new_page("Medication schedule", "Current medicines and supplements")
    for _ in range(6):
        doc.row_fields([("Medicine", 150), ("Dose", 80), ("Times / day", 80), ("With food?", 80)], h=14)
        doc.labeled_field("Purpose / notes", doc.width - 72, 22)
    doc.footer()

    doc.new_page("Medication dose log", "Use during hard weeks or new prescriptions")
    doc.row_fields([("Pet name", 180), ("Medicine", 220)])
    for _ in range(12):
        doc.row_fields([("Date / time", 120), ("Dose given", 100), ("By whom", 120), ("Notes", 140)], h=14)
    doc.footer("For ongoing illness tracking, also use free condition trackers on the website.")

    # 10-11 Vet visits
    doc.new_page("Vet visit log", "What happened and what to follow up")
    for _ in range(3):
        doc.row_fields([("Date", 90), ("Clinic / doctor", 180), ("Weight", 80)])
        doc.labeled_field("Reason for visit", doc.width - 72, 22)
        doc.labeled_field("Findings / plan", doc.width - 72, 36)
        doc.labeled_field("Follow-up / next appointment", doc.width - 72, 22)
        doc.y -= 6
    doc.footer()

    doc.new_page("Vet visit log (continued)", "")
    for _ in range(3):
        doc.row_fields([("Date", 90), ("Clinic / doctor", 180), ("Weight", 80)])
        doc.labeled_field("Reason for visit", doc.width - 72, 22)
        doc.labeled_field("Findings / plan", doc.width - 72, 36)
        doc.labeled_field("Follow-up / next appointment", doc.width - 72, 22)
        doc.y -= 6
    doc.footer()

    # 12 Weight
    doc.new_page("Weight & body condition", "Track trends between visits")
    for _ in range(14):
        doc.row_fields([("Date", 90), ("Weight", 80), ("Body condition notes", 280)], h=14)
    doc.footer()

    # 13 Grooming
    doc.new_page("Grooming log", "Baths, nails, ears, teeth, coat")
    for _ in range(12):
        doc.row_fields([("Date", 80), ("Service", 140), ("Provider", 120), ("Notes", 160)], h=14)
    doc.footer()

    # 14-15 Feeding
    doc.new_page("Feeding plan", "What they eat and how much")
    doc.row_fields([("Food brand / formula", 260), ("Amount per meal", 160)])
    doc.row_fields([("Meals per day", 120), ("Treat rules", 300)])
    doc.labeled_field("Dietary restrictions", doc.width - 72, 36)
    doc.labeled_field("Water / hydration notes", doc.width - 72, 36)
    doc.section("Weekly feeding check-off")
    doc.c.setFillColor(INK)
    doc.c.setFont("Helvetica", 8)
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    doc.c.drawString(36, doc.y, "Meal")
    x = 100
    for day in days:
        doc.c.drawString(x, doc.y, day)
        x += 55
    doc.y -= 16
    for meal in ("Breakfast", "Lunch", "Dinner", "Meds with food", "Fresh water"):
        doc.c.setFillColor(INK)
        doc.c.setFont("Helvetica", 8)
        doc.c.drawString(36, doc.y, meal)
        x = 100
        for _ in days:
            name = doc._fid("c")
            doc.c.acroForm.checkbox(name=name, x=x, y=doc.y - 2, size=9, borderColor=LINE, fillColor=white, checked=False)
            x += 55
        doc.y -= 18
    doc.footer()

    doc.new_page("Supply checklist", "Food, litter, meds, and gear to keep stocked")
    doc.checkbox_row(["Food", "Treats", "Litter / pads", "Waste bags"])
    doc.checkbox_row(["Medicines", "Preventatives", "First aid", "Cleaning supplies"])
    doc.checkbox_row(["Leash / carrier", "Beds / blankets", "Toys", "ID tags"])
    doc.labeled_field("Brand preferences / where you buy", doc.width - 72, 48)
    doc.labeled_field("Running low / buy next", doc.width - 72, 60)
    doc.footer()

    # 16 Expenses
    doc.new_page("Care expenses", "Optional budget tracking")
    for _ in range(14):
        doc.row_fields([("Date", 80), ("Category", 120), ("Amount", 80), ("Notes", 200)], h=14)
    doc.footer()

    # 17-21 Sitter handbook
    doc.new_page("Sitter handbook — overview", "Hand these pages to anyone watching your pets")
    doc.row_fields([("Dates of care", 200), ("Number of pets", 120)])
    doc.labeled_field("Household address / access notes", doc.width - 72, 36)
    doc.labeled_field("Wi‑Fi / alarm / parking (optional)", doc.width - 72, 36)
    doc.labeled_field("What “a good day” looks like", doc.width - 72, 48)
    doc.labeled_field("What needs an urgent call or ER visit", doc.width - 72, 48)
    doc.footer()

    doc.new_page("Sitter handbook — daily routine", "")
    doc.labeled_field("Morning routine", doc.width - 72, 54)
    doc.labeled_field("Midday / afternoon", doc.width - 72, 54)
    doc.labeled_field("Evening / bedtime", doc.width - 72, 54)
    doc.labeled_field("Walks / play / enrichment", doc.width - 72, 40)
    doc.footer()

    doc.new_page("Sitter handbook — behavior & handling", "")
    doc.labeled_field("Friendly with strangers / other animals?", doc.width - 72, 36)
    doc.labeled_field("Triggers, fears, or no-go situations", doc.width - 72, 48)
    doc.labeled_field("How to give medicine or handle carrier / leash", doc.width - 72, 48)
    doc.labeled_field("House training / litter notes", doc.width - 72, 36)
    doc.footer()

    doc.new_page("Sitter handbook — house rules", "")
    doc.labeled_field("Rooms that are off-limits", doc.width - 72, 36)
    doc.labeled_field("Furniture / furniture rules", doc.width - 72, 36)
    doc.labeled_field("Trash, plants, and hazards to watch", doc.width - 72, 48)
    doc.labeled_field("Visitors, deliveries, and quiet hours", doc.width - 72, 36)
    doc.footer()

    doc.new_page("Sitter emergency authorization", "Complete before you leave")
    doc.labeled_field("I authorize the sitter to seek veterinary care if I cannot be reached", doc.width - 72, 36)
    doc.row_fields([("Spending limit (if any)", 180), ("Preferred ER clinic", 220)])
    doc.row_fields([("Owner signature / typed name", 240), ("Date", 120)])
    doc.row_fields([("Sitter name", 200), ("Sitter phone", 160)])
    doc.labeled_field("Additional authorization notes", doc.width - 72, 60)
    doc.footer()

    # 22 Travel
    doc.new_page("Travel go-bag checklist", "Ready for trips, evacuations, or ER visits")
    doc.checkbox_row(["Food 3+ days", "Water bowl", "Medicines", "Preventatives"])
    doc.checkbox_row(["Leash / carrier", "Waste bags", "Litter / pads", "Blankets"])
    doc.checkbox_row(["Vaccine records", "Microchip info", "Insurance card", "Photo of pet"])
    doc.checkbox_row(["First aid", "Toys", "Treats", "Cleanup kit"])
    doc.labeled_field("Packing notes for this household", doc.width - 72, 70)
    doc.footer()

    # 23 Handover checklist
    doc.new_page("Departure & return checklist", "Before you leave and when you get home")
    doc.section("Before departure")
    doc.checkbox_row(["Meds refilled", "Food stocked", "Keys shared", "ER plan reviewed"])
    doc.checkbox_row(["Sitter walkthrough", "Contacts updated", "Litter clean", "Trash out"])
    doc.section("During care — sitter notes")
    doc.labeled_field("Day-by-day notes for the owner", doc.width - 72, 90)
    doc.section("On return")
    doc.checkbox_row(["Meds left", "Supplies used", "Incidents noted", "Keys returned"])
    doc.footer()

    # Dental / procedures / annual review (extra depth vs thin $3–$5 planners)
    doc.new_page("Dental & procedure history", "Surgeries, dental work, and hospital stays")
    for _ in range(8):
        doc.row_fields([("Date", 80), ("Procedure", 160), ("Clinic", 140), ("Notes", 120)], h=16)
    doc.labeled_field("Anesthesia / recovery notes", doc.width - 72, 48)
    doc.footer()

    doc.new_page("Annual health review", "Yearly snapshot to discuss with the veterinary team")
    doc.row_fields([("Year", 80), ("Pet name", 180), ("Current weight", 100)])
    doc.labeled_field("Biggest health wins this year", doc.width - 72, 40)
    doc.labeled_field("Ongoing concerns", doc.width - 72, 48)
    doc.labeled_field("Lifestyle changes (diet, home, new pets)", doc.width - 72, 40)
    doc.labeled_field("Questions for the next wellness visit", doc.width - 72, 60)
    doc.footer()

    doc.new_page("Quality-of-life notes", "For senior pets or hard seasons — organization only, not a score")
    doc.labeled_field("Good-day signs", doc.width - 72, 48)
    doc.labeled_field("Hard-day signs", doc.width - 72, 48)
    doc.labeled_field("Comfort / mobility / appetite observations", doc.width - 72, 60)
    doc.labeled_field("Questions for the veterinary team", doc.width - 72, 48)
    doc.footer("For day-to-day illness logging, use free condition trackers on the website.")

    doc.new_page("Second pet quick profile", "Duplicate the full profile pages for each pet; use this for a fast second sheet")
    doc.row_fields([("Pet name", 180), ("Species / breed", 200)])
    doc.row_fields([("Microchip", 180), ("Insurance policy #", 200)])
    doc.row_fields([("Primary clinic phone", 180), ("ER clinic phone", 200)])
    doc.labeled_field("Meds summary", doc.width - 72, 48)
    doc.labeled_field("Behavior / handling notes for sitters", doc.width - 72, 60)
    doc.footer("Print additional full profile pages as needed.")

    # Notes + index
    doc.new_page("Extra notes", "Anything else caregivers should know")
    doc.field(doc.width - 72, 520, multiline=True)
    doc.footer()

    doc.new_page("Household pet index", "One line per pet so sitters see the whole home at a glance")
    for _ in range(8):
        doc.row_fields([("Pet name", 120), ("Species", 80), ("Main concern", 160), ("Page / binder #", 80)], h=16)
    doc.labeled_field("Household notes", doc.width - 72, 80)
    doc.footer("Pair with free condition trackers and Quick Phone Log on Your Pet’s Health Log.")


def build_format(label: str, pagesize) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"household-pet-care-binder-{label.lower().replace(' ', '-')}.pdf"
    doc = BinderCanvas(path, pagesize)
    build_pages(doc)
    doc.save()
    LOGGER.info("Wrote %s (%d pages)", path.name, doc.page_no)
    return path


def build_zip(paths: list[Path], meta: dict) -> Path:
    zip_path = OUT / f"{meta['id']}.zip"
    readme = OUT / "README.txt"
    readme.write_text(
        "\n".join(
            [
                meta["title"],
                f"Price target: {meta['price_display']}",
                "",
                meta["blurb"],
                "",
                "Includes:",
                "- household-pet-care-binder-us-letter.pdf (fillable)",
                "- household-pet-care-binder-a4.pdf (fillable)",
                "",
                "The free Your Pet’s Health Log site keeps the 72 condition trackers and Quick Phone Log.",
                "This binder is household paperwork and sitter handover — not a reprint of those free PDFs.",
                "",
                f"Site: https://{SITE}/",
            ]
        ),
        encoding="utf-8",
    )
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(readme, arcname="README.txt")
        for path in paths:
            zf.write(path, arcname=path.name)
    LOGGER.info("Wrote fulfillment ZIP %s", zip_path.name)
    return zip_path


def main() -> int:
    try:
        meta = json.loads(META_PATH.read_text(encoding="utf-8"))
        letter_pdf = build_format("US Letter", letter)
        a4_pdf = build_format("A4", A4)
        build_zip([letter_pdf, a4_pdf], meta)
        LOGGER.info("Household binder ready for Gumroad upload at $12–$15")
        return 0
    except Exception:
        LOGGER.exception("Household binder build failed")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
