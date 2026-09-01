"""Production certification for the Steady Paws static site and generated PDF library."""

from __future__ import annotations

import logging
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

from pypdf import PdfReader

from tracker_catalog import GROUP_LABELS, TRACKERS

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
LOGGER = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SITE_URL = "https://steadypaws.netlify.app/"
EXPECTED_SUPPORT_URL = "https://buymeacoffee.com/divclass016"


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.targets: list[str] = []
        self.h1_count = 0
        self.tracker_cards = 0
        self.family_choices = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        classes = values.get("class") or ""
        if tag == "h1":
            self.h1_count += 1
        if tag == "article" and "tracker-card" in classes:
            self.tracker_cards += 1
        if tag == "button" and "family-choice" in classes:
            self.family_choices += 1
        for key in ("href", "src"):
            value = values.get(key)
            if value:
                self.targets.append(value)


def assert_catalog() -> None:
    filenames = [item["filename"] for item in TRACKERS]
    if len(TRACKERS) != 72:
        raise AssertionError(f"Expected 72 trackers, found {len(TRACKERS)}")
    if len(filenames) != len(set(filenames)):
        raise AssertionError("Duplicate tracker filenames in catalog")
    allowed_groups = set(GROUP_LABELS) - {"all"}
    unknown = sorted({item["group"] for item in TRACKERS} - allowed_groups)
    if unknown:
        raise AssertionError(f"Unknown tracker groups: {unknown}")
    LOGGER.info("Shared 72-tracker catalog: PASS")


def assert_required_files() -> None:
    required = (
        "index.html", "404.html", "styles/base.css", "styles/components.css",
        "assets/paw.svg", "assets/site.js", "netlify.toml", "robots.txt", "sitemap.xml",
        "requirements.txt", "templates/index.template.html", "scripts/tracker_catalog.py",
        "scripts/build_trackers.py", "scripts/build_site.py",
    )
    missing = [path for path in required if not (ROOT / path).is_file()]
    if missing:
        raise AssertionError(f"Missing required files: {', '.join(missing)}")
    LOGGER.info("Required production files: PASS")


def assert_homepage() -> None:
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    required_markers = (
        'lang="en"', 'name="viewport"', 'name="description"',
        'name="robots" content="index, follow"',
        f'rel="canonical" href="{EXPECTED_SITE_URL}"',
        f'property="og:url" content="{EXPECTED_SITE_URL}"',
        EXPECTED_SUPPORT_URL,
        "Care paperwork for someone you love",
        "Who are we caring for today?",
        "What tough time are they going through?",
        "Get their tracker",
    )
    missing = [marker for marker in required_markers if marker not in html]
    if missing:
        raise AssertionError(f"Homepage markers missing: {missing}")
    if "In development" in html or "buymeacoffee.com/yourname" in html:
        raise AssertionError("Homepage contains unfinished placeholder content")

    parser = LinkParser()
    parser.feed(html)
    if parser.h1_count != 1:
        raise AssertionError(f"Expected exactly one h1, found {parser.h1_count}")
    if parser.tracker_cards != len(TRACKERS):
        raise AssertionError(f"Expected {len(TRACKERS)} tracker cards, found {parser.tracker_cards}")
    if parser.family_choices < 13:
        raise AssertionError(f"Expected broad family-member picker, found {parser.family_choices} choices")

    for item in TRACKERS:
        expected = f'/downloads/{item["filename"]}'
        if expected not in html:
            raise AssertionError(f"Homepage missing tracker link: {expected}")

    for target in parser.targets:
        parsed = urlparse(target)
        if parsed.scheme or target.startswith("#"):
            continue
        clean = parsed.path.lstrip("/")
        if clean and not (ROOT / clean).exists():
            raise AssertionError(f"Broken local reference: {target}")
    LOGGER.info("Family-first homepage, cards, and local references: PASS")


def assert_search_files() -> None:
    robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    if f"Sitemap: {EXPECTED_SITE_URL}sitemap.xml" not in robots:
        raise AssertionError("robots.txt does not advertise the production sitemap")
    if f"<loc>{EXPECTED_SITE_URL}</loc>" not in sitemap:
        raise AssertionError("sitemap.xml does not contain production homepage URL")
    LOGGER.info("Canonical crawler files: PASS")


def assert_pdfs() -> None:
    for item in TRACKERS:
        pdf = ROOT / "downloads" / item["filename"]
        if not pdf.is_file() or pdf.stat().st_size < 1000:
            raise AssertionError(f"Missing or unexpectedly small PDF: {item['filename']}")
        if pdf.read_bytes()[:5] != b"%PDF-":
            raise AssertionError(f"Invalid PDF signature: {item['filename']}")
        pages = len(PdfReader(str(pdf)).pages)
        if pages != 2:
            raise AssertionError(f"Expected 2 pages, found {pages}: {item['filename']}")
    LOGGER.info("All 72 printable PDFs (2 pages each): PASS")


def main() -> int:
    try:
        assert_catalog()
        assert_required_files()
        assert_homepage()
        assert_search_files()
        assert_pdfs()
        LOGGER.info("STEADY PAWS QUALITY GATE: PASS")
        return 0
    except Exception as exc:
        LOGGER.exception("STEADY PAWS QUALITY GATE: FAIL: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
