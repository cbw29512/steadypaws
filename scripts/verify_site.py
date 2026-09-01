"""Production certification for the Steady Paws site and generated care-paperwork library."""

from __future__ import annotations

import logging
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

from pypdf import PdfReader

from tracker_catalog import CONDITION_NAMES, GROUP_LABELS, TRACKERS, condition_name

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
LOGGER = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SITE_URL = "https://steadypaws.netlify.app/"
EXPECTED_SUPPORT_URL = "https://buymeacoffee.com/divclass016"
EXPECTED_ASSET_REV = "20260901-primary1"


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.targets: list[str] = []
        self.h1_count = 0
        self.condition_cards = 0
        self.condition_keys: list[str] = []
        self.form_variants = 0
        self.family_choices = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        classes = values.get("class") or ""
        if tag == "h1":
            self.h1_count += 1
        if tag == "article" and "condition-card" in classes:
            self.condition_cards += 1
            key = values.get("data-condition")
            if key:
                self.condition_keys.append(key)
        if tag == "div" and "tracker-variant" in classes:
            self.form_variants += 1
        if tag == "button" and "family-choice" in classes:
            self.family_choices += 1
        for key in ("href", "src"):
            value = values.get(key)
            if value:
                self.targets.append(value)


def assert_catalog() -> None:
    filenames = [item["filename"] for item in TRACKERS]
    if len(TRACKERS) != 72:
        raise AssertionError(f"Expected 72 tailored care forms, found {len(TRACKERS)}")
    if len(filenames) != len(set(filenames)):
        raise AssertionError("Duplicate care-form filenames in catalog")
    allowed_groups = set(GROUP_LABELS) - {"all"}
    unknown = sorted({item["group"] for item in TRACKERS} - allowed_groups)
    if unknown:
        raise AssertionError(f"Unknown care-form groups: {unknown}")
    if len(CONDITION_NAMES) >= len(TRACKERS):
        raise AssertionError("Health concerns were not deduplicated across tailored species variants")

    by_filename = {item["filename"]: item for item in TRACKERS}
    shared_sets = (
        ("diabetic-cat-tracker.pdf", "dog-diabetes-tracker.pdf"),
        ("cat-arthritis-mobility-tracker.pdf", "dog-arthritis-mobility-tracker.pdf", "rabbit-arthritis-mobility-tracker.pdf"),
        ("cat-heart-disease-tracker.pdf", "dog-heart-disease-tracker.pdf", "ferret-heart-disease-tracker.pdf"),
        ("rabbit-dental-disease-tracker.pdf", "guinea-pig-dental-tracker.pdf", "chinchilla-dental-tracker.pdf"),
        ("cat-cancer-supportive-care-tracker.pdf", "dog-cancer-supportive-care-tracker.pdf", "ferret-cancer-supportive-care-tracker.pdf"),
        ("guinea-pig-respiratory-tracker.pdf", "chinchilla-respiratory-tracker.pdf", "bird-respiratory-tracker.pdf", "reptile-respiratory-tracker.pdf"),
        ("reptile-metabolic-bone-tracker.pdf", "amphibian-metabolic-bone-tracker.pdf"),
    )
    for filenames_to_compare in shared_sets:
        names = {condition_name(by_filename[name]) for name in filenames_to_compare}
        if len(names) != 1:
            raise AssertionError(f"Shared health concern split into duplicate names: {filenames_to_compare} -> {sorted(names)}")
    LOGGER.info("72 tailored forms normalized into shared primary health concerns: PASS")


def assert_required_files() -> None:
    required = (
        "index.html", "404.html", "styles/base.css", "styles/components.css", "styles/family.css",
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
        "Your family member's care paperwork",
        "Pick your family member.",
        "What is the biggest health concern right now?",
        "Primary health concern",
        "other conditions they are living with",
        "Get their care paperwork",
        "Someone else",
        "View all concerns",
        f'/styles/base.css?v={EXPECTED_ASSET_REV}',
        f'/styles/components.css?v={EXPECTED_ASSET_REV}',
        f'/styles/family.css?v={EXPECTED_ASSET_REV}',
        f'/assets/site.js?v={EXPECTED_ASSET_REV}',
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
    if parser.condition_cards != len(CONDITION_NAMES):
        raise AssertionError(
            f"Expected {len(CONDITION_NAMES)} unique health-concern cards, found {parser.condition_cards}"
        )
    if len(parser.condition_keys) != len(set(parser.condition_keys)):
        raise AssertionError("Duplicate primary health-concern cards rendered on homepage")
    if parser.form_variants != len(TRACKERS):
        raise AssertionError(f"Expected {len(TRACKERS)} tailored form variants, found {parser.form_variants}")
    if parser.family_choices < 13:
        raise AssertionError(f"Expected broad family-member picker, found {parser.family_choices} choices")

    for item in TRACKERS:
        expected = f'/downloads/{item["filename"]}'
        if expected not in html:
            raise AssertionError(f"Homepage missing tailored care-form link: {expected}")

    for target in parser.targets:
        parsed = urlparse(target)
        if parsed.scheme or target.startswith("#"):
            continue
        clean = parsed.path.lstrip("/")
        if clean and not (ROOT / clean).exists():
            raise AssertionError(f"Broken local reference: {target}")
    LOGGER.info("Unique health concerns, tailored variants, guided picker, and versioned assets: PASS")


def assert_family_picker_styles() -> None:
    components = (ROOT / "styles/components.css").read_text(encoding="utf-8")
    family = (ROOT / "styles/family.css").read_text(encoding="utf-8")
    for marker in (".family-choice {", ".family-choice.is-selected", ".family-grid {"):
        if marker not in components:
            raise AssertionError(f"Core family picker style missing from components.css: {marker}")
    for marker in (".family-more {", ".family-grid-primary", ".family-grid-more", ".tracker-variant {", ".condition-kicker"):
        if marker not in family:
            raise AssertionError(f"Family/condition style missing from family.css: {marker}")

    netlify = (ROOT / "netlify.toml").read_text(encoding="utf-8")
    if 'for = "/styles/*"' not in netlify or 'for = "/assets/*"' not in netlify:
        raise AssertionError("Netlify cache rules for styles/assets are missing")
    if netlify.count('Cache-Control = "public, max-age=0, must-revalidate"') < 2:
        raise AssertionError("CSS/JS must revalidate so deploys cannot mix stale and new UI assets")
    if 'for = "/styles/*"\n  [headers.values]\n    Cache-Control = "public, max-age=604800"' in netlify:
        raise AssertionError("Styles are still configured for week-long stale caching")
    LOGGER.info("Family picker, condition variants, and deployment cache policy: PASS")


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
        reader = PdfReader(str(pdf))
        if len(reader.pages) != 2:
            raise AssertionError(f"Expected 2 pages, found {len(reader.pages)}: {item['filename']}")
        first_page = reader.pages[0].extract_text() or ""
        second_page = reader.pages[1].extract_text() or ""
        for marker in ("Their name", "Primary health concern", "Other conditions they're living with", condition_name(item)):
            if marker not in first_page:
                raise AssertionError(f"Primary/multi-condition wording missing from {item['filename']}: {marker}")
        if "How they did this week" not in second_page:
            raise AssertionError(f"Family-first weekly wording missing: {item['filename']}")
    LOGGER.info("All 72 tailored PDFs include primary + other-condition context (144 pages): PASS")


def main() -> int:
    try:
        assert_catalog()
        assert_required_files()
        assert_homepage()
        assert_family_picker_styles()
        assert_search_files()
        assert_pdfs()
        LOGGER.info("STEADY PAWS QUALITY GATE: PASS")
        return 0
    except Exception as exc:
        LOGGER.exception("STEADY PAWS QUALITY GATE: FAIL: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
