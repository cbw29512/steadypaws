"""Production certification for Steady Paws SEO, caregiver UX, downloads, privacy, and build integrity."""

from __future__ import annotations

import base64
import hashlib
import logging
import xml.etree.ElementTree as ET
from html import escape
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
EXPECTED_ASSET_REV = "20260901-pawphoto1"
CARE_ASSET_REV = "20260901-printphoto2"
EXPECTED_VENDOR_SHA512 = "z8IYLHO8bTgFqj+yrPyIJnzBDf7DDhWwiEsk4sY+Oe6J2M+WQequeGS7qioI5vT6rXgVRb4K1UVQC5ER7MKzKQ=="
VENDOR_PATH = ROOT / "assets/vendor/pdf-lib-1.17.1.min.js"


class HomeParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.targets: list[str] = []
        self.h1_count = 0
        self.condition_cards = 0
        self.condition_keys: list[str] = []
        self.form_variants = 0
        self.family_choices = 0
        self.care_downloads = 0
        self.accessible_links = 0
        self.photo_inputs = 0
        self.brand_logos = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        classes = set((values.get("class") or "").split())
        if tag == "h1":
            self.h1_count += 1
        if tag == "article" and "condition-card" in classes:
            self.condition_cards += 1
            if values.get("data-condition"):
                self.condition_keys.append(values["data-condition"] or "")
        if tag == "div" and "tracker-variant" in classes:
            self.form_variants += 1
        if tag == "button" and "family-choice" in classes:
            self.family_choices += 1
        if tag == "a" and "care-download" in classes:
            self.care_downloads += 1
        if tag == "a" and "accessible-link" in classes:
            self.accessible_links += 1
        if tag == "input" and values.get("id") == "family-photo" and values.get("type") == "file":
            self.photo_inputs += 1
        if tag == "img" and "brand-logo" in classes:
            self.brand_logos += 1
        for key in ("href", "src"):
            value = values.get(key)
            if value:
                self.targets.append(value)


def care_page_path(item: dict) -> Path:
    return ROOT / "care" / f"{Path(item['filename']).stem}.html"


def care_page_url(item: dict) -> str:
    return f"{EXPECTED_SITE_URL.rstrip('/')}/care/{Path(item['filename']).stem}.html"


def assert_catalog() -> None:
    filenames = [item["filename"] for item in TRACKERS]
    if len(TRACKERS) != 72:
        raise AssertionError(f"Expected 72 tailored care forms, found {len(TRACKERS)}")
    if len(CONDITION_NAMES) != 40:
        raise AssertionError(f"Expected 40 deduplicated health concerns, found {len(CONDITION_NAMES)}")
    if len(filenames) != len(set(filenames)):
        raise AssertionError("Duplicate care-form filenames in catalog")
    allowed_groups = set(GROUP_LABELS) - {"all"}
    unknown = sorted({item["group"] for item in TRACKERS} - allowed_groups)
    if unknown:
        raise AssertionError(f"Unknown care-form groups: {unknown}")

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
    for group in shared_sets:
        names = {condition_name(by_filename[name]) for name in group}
        if len(names) != 1:
            raise AssertionError(f"Shared concern split into duplicate names: {group} -> {sorted(names)}")
    LOGGER.info("40 unique concerns / 72 tailored variants: PASS")


def assert_required_files() -> None:
    required = (
        "index.html", "404.html", "accessibility.html", "privacy.html",
        "styles/base.css", "styles/components.css", "styles/family.css", "styles/care.css",
        "assets/paw.svg", "assets/site.js", "assets/personalization-bridge-print1.js",
        "assets/care-personalization-print1.js", "assets/vendor/pdf-lib-1.17.1.min.js",
        "netlify.toml", "robots.txt", "sitemap.xml", "requirements.txt",
        "templates/index.template.html", "scripts/tracker_catalog.py", "scripts/fetch_vendor.py",
        "scripts/build_trackers.py", "scripts/build_site.py", "scripts/build_accessible_pages.py",
        "scripts/verify_accessibility.py", "scripts/verify_personalization.py", "scripts/serve_ci.py",
    )
    missing = [path for path in required if not (ROOT / path).is_file()]
    if missing:
        raise AssertionError(f"Missing required files: {', '.join(missing)}")
    if len(list((ROOT / "care").glob("*.html"))) != len(TRACKERS):
        raise AssertionError("Accessible care-page count does not match catalog")
    LOGGER.info("Required production files + 72 accessible worksheets: PASS")


def assert_vendor_and_paw() -> None:
    digest = base64.b64encode(hashlib.sha512(VENDOR_PATH.read_bytes()).digest()).decode("ascii")
    if digest != EXPECTED_VENDOR_SHA512:
        raise AssertionError("Self-hosted pdf-lib bytes do not match pinned SHA-512")
    svg = (ROOT / "assets/paw.svg").read_text(encoding="utf-8")
    for marker in ('aria-label="Steady Paws paw logo"', 'fill="#55756c"', 'fill="#fffdf9"'):
        if marker not in svg:
            raise AssertionError(f"Paw logo marker missing: {marker}")
    if svg.count("<ellipse") < 5:
        raise AssertionError("Paw logo is incomplete")
    LOGGER.info("Pinned personalization helper + paw logo: PASS")


def assert_homepage() -> None:
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    required = (
        '<title>Free Pet Health Trackers & Care Paperwork | Steady Paws</title>',
        'name="robots" content="index, follow, max-image-preview:large"',
        f'rel="canonical" href="{EXPECTED_SITE_URL}"', f'property="og:url" content="{EXPECTED_SITE_URL}"',
        EXPECTED_SUPPORT_URL, "Your family member's care paperwork", "Pick your family member.",
        "What is the biggest health concern right now?", "Make their paperwork feel like theirs.",
        "Private by design", "Accessible web worksheet", "Someone else", "View all concerns",
        'id="family-name"', 'id="family-photo"', 'type="file"', 'accept="image/*"',
        f'/assets/paw.svg?v={EXPECTED_ASSET_REV}', f'/assets/site.js?v={EXPECTED_ASSET_REV}',
        '/assets/personalization-bridge-print1.js',
    )
    missing = [marker for marker in required if marker not in html]
    if missing:
        raise AssertionError(f"Homepage production markers missing: {missing}")
    for forbidden in ("In development", "buymeacoffee.com/yourname", "cdn.jsdelivr.net", "<script>", "style="):
        if forbidden in html:
            raise AssertionError(f"Homepage contains forbidden marker: {forbidden}")

    parser = HomeParser()
    parser.feed(html)
    if parser.h1_count != 1:
        raise AssertionError(f"Expected one h1, found {parser.h1_count}")
    if parser.condition_cards != len(CONDITION_NAMES) or len(parser.condition_keys) != len(set(parser.condition_keys)):
        raise AssertionError("Homepage health-concern cards are duplicated or incomplete")
    if parser.form_variants != len(TRACKERS) or parser.care_downloads != len(TRACKERS) or parser.accessible_links != len(TRACKERS):
        raise AssertionError("Homepage resource count does not match catalog")
    if parser.photo_inputs != 1 or parser.family_choices < 13 or parser.brand_logos != 1:
        raise AssertionError("Family picker, paw branding, or photo personalization is incomplete")
    for target in parser.targets:
        parsed = urlparse(target)
        if parsed.scheme or target.startswith("#"):
            continue
        clean = parsed.path.lstrip("/")
        if clean and not (ROOT / clean).exists():
            raise AssertionError(f"Broken local reference: {target}")
    LOGGER.info("Homepage SEO, dedupe, family picker, photo flow, and links: PASS")


def assert_personalization_source() -> None:
    site_js = (ROOT / "assets/site.js").read_text(encoding="utf-8")
    bridge_js = (ROOT / "assets/personalization-bridge-print1.js").read_text(encoding="utf-8")
    care_js = (ROOT / "assets/care-personalization-print1.js").read_text(encoding="utf-8")
    for marker in (
        "Photo ready ✓", "Personalized PDF ready ✓", "embedJpg", "page.drawImage(photo, PHOTO_IMAGE_BOX)",
        "const PHOTO_IMAGE_BOX = { x: 490, y: 607, width: 82, height: 82 }",
        "const NAME_POSITION = { x: 96, y: 666, maxWidth: 190 }",
    ):
        if marker not in site_js:
            raise AssertionError(f"Homepage personalization marker missing: {marker}")
    for marker in ("sessionStorage", "steadypaws.personalization.v1", "accessibleLinks", "MutationObserver"):
        if marker not in bridge_js:
            raise AssertionError(f"Personalization bridge marker missing: {marker}")
    for marker in (
        "sessionStorage", "care-family-photo", "care-print-personalized", "embedJpg",
        "page.drawImage(photo, PHOTO_IMAGE_BOX)",
    ):
        if marker not in care_js:
            raise AssertionError(f"Care-page personalization marker missing: {marker}")
    LOGGER.info("Local photo/name personalization across PDF + browser print paths: PASS")


def assert_print_design_source() -> None:
    source = (ROOT / "scripts/build_trackers.py").read_text(encoding="utf-8")
    required = (
        "GROUP_ACCENTS", "draw_paw_mark", "CARE DETAILS", "Main health concern", "Other health conditions",
        "Daily care log", "Use one row each time you check or give care.", "Date / time",
        "This week at a glance", "Since the last vet visit", "Questions for the vet",
        "Plan / next steps from the vet", "For organizing care, not medical advice.",
        "PHOTO_IMAGE_BOX = (490, 607, 82, 82)", "NAME_TEXT_POSITION = (96, 666)",
    )
    missing = [marker for marker in required if marker not in source]
    if missing:
        raise AssertionError(f"KISS print-design markers missing: {missing}")
    for forbidden in ("ABOUT YOUR FAMILY MEMBER", "11 ENTRIES", 'c.drawString(x0, y_top + 13, "Daily observations")'):
        if forbidden in source:
            raise AssertionError(f"Old high-cognitive-load print wording returned: {forbidden}")
    LOGGER.info("Soft paw-branded KISS print design source: PASS")


def assert_accessible_care_pages() -> None:
    required_copy = (
        "Care details", "Main health concern", "Other health conditions", "Daily care log",
        "This week at a glance", "Since the last vet visit", "Questions for the vet", "Plan / next steps from the vet",
    )
    for item in TRACKERS:
        path = care_page_path(item)
        html = path.read_text(encoding="utf-8")
        required = (
            'lang="en"', 'name="viewport"', 'name="description"',
            'name="robots" content="index, follow, max-image-preview:large"',
            f'rel="canonical" href="{care_page_url(item)}"',
            f'rel="alternate" type="application/pdf" href="/downloads/{item["filename"]}"',
            '<main id="main"', '<fieldset', '<legend>', '<caption id="daily-caption">', '<th scope="col">',
            'class="brand-logo"', f'/styles/care.css?v={CARE_ASSET_REV}',
            f'/assets/care-personalization-print1.js?v={CARE_ASSET_REV}',
            'id="care-family-name"', 'id="care-print-personalized"', 'id="care-personalization-status"',
            escape(condition_name(item)), escape(item["species"]), '/accessibility.html', '/privacy.html',
            *required_copy,
        )
        missing = [marker for marker in required if marker not in html]
        if missing:
            raise AssertionError(f"Accessible page markers missing from {path.name}: {missing}")
        if "style=" in html:
            raise AssertionError(f"Accessible page contains inline style: {path.name}")
    LOGGER.info("72 accessible worksheets use the same calm KISS language: PASS")


def assert_security_sitemap_and_static_pages() -> None:
    for filename in ("404.html", "accessibility.html", "privacy.html"):
        html = (ROOT / filename).read_text(encoding="utf-8")
        if f'/assets/paw.svg?v={EXPECTED_ASSET_REV}' not in html:
            raise AssertionError(f"Stale branding asset in {filename}")
    netlify = (ROOT / "netlify.toml").read_text(encoding="utf-8")
    required = (
        "python scripts/fetch_vendor.py", "python scripts/build_accessible_pages.py", "Strict-Transport-Security",
        'X-Frame-Options = "DENY"', "script-src 'self'", "connect-src 'self'", "img-src 'self' data: blob:",
        "object-src 'none'", "frame-ancestors 'none'", 'for = "/styles/*"', 'for = "/assets/*"',
    )
    missing = [marker for marker in required if marker not in netlify]
    if missing:
        raise AssertionError(f"Security/build policy markers missing: {missing}")
    if "cdn.jsdelivr.net" in netlify or "enhance_accessible_pages.py" in netlify:
        raise AssertionError("Runtime/build still references a retired dependency path")

    robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
    if f"Sitemap: {EXPECTED_SITE_URL}sitemap.xml" not in robots:
        raise AssertionError("robots.txt does not advertise production sitemap")
    root = ET.parse(ROOT / "sitemap.xml").getroot()
    namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [node.text for node in root.findall("s:url/s:loc", namespace) if node.text]
    expected = {EXPECTED_SITE_URL, f"{EXPECTED_SITE_URL}accessibility.html", f"{EXPECTED_SITE_URL}privacy.html", *(care_page_url(item) for item in TRACKERS)}
    if len(urls) != 75 or set(urls) != expected:
        raise AssertionError("Sitemap must contain exactly 75 canonical URLs")
    LOGGER.info("Security, cache policy, static pages, robots, and sitemap: PASS")


def assert_pdfs() -> None:
    for item in TRACKERS:
        pdf = ROOT / "downloads" / item["filename"]
        if not pdf.is_file() or pdf.stat().st_size < 1000 or pdf.read_bytes()[:5] != b"%PDF-":
            raise AssertionError(f"Missing or invalid PDF: {item['filename']}")
        reader = PdfReader(str(pdf))
        if len(reader.pages) != 2:
            raise AssertionError(f"Expected 2 pages: {item['filename']}")
        first_page = reader.pages[0].extract_text() or ""
        second_page = reader.pages[1].extract_text() or ""
        for marker in (
            "Their name", "Main health concern", "Other health conditions", "THEIR PHOTO", "optional",
            "Daily care log", "Date / time", condition_name(item),
        ):
            if marker not in first_page:
                raise AssertionError(f"Printable PDF marker missing from {item['filename']}: {marker}")
        for marker in ("This week at a glance", "Since the last vet visit", "Questions for the vet", "Plan / next steps from the vet"):
            if marker not in second_page:
                raise AssertionError(f"Page 2 marker missing from {item['filename']}: {marker}")
        if "*" in first_page:
            raise AssertionError(f"Ambiguous asterisk marker remains on printable sheet: {item['filename']}")
        if str(reader.root_object.get("/Lang")) != "en-US":
            raise AssertionError(f"PDF language metadata missing: {item['filename']}")
        if not reader.metadata or not reader.metadata.title or len(reader.outline) < 2:
            raise AssertionError(f"PDF metadata/bookmarks missing: {item['filename']}")
    LOGGER.info("72 two-page KISS print PDFs with paw/photo space + metadata (144 pages): PASS")


def main() -> int:
    try:
        assert_catalog()
        assert_required_files()
        assert_vendor_and_paw()
        assert_homepage()
        assert_personalization_source()
        assert_print_design_source()
        assert_accessible_care_pages()
        assert_security_sitemap_and_static_pages()
        assert_pdfs()
        LOGGER.info("STEADY PAWS PRODUCTION QUALITY GATE: PASS")
        return 0
    except Exception as exc:
        LOGGER.exception("STEADY PAWS PRODUCTION QUALITY GATE: FAIL: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
