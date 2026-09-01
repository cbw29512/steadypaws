"""Static production checks for the Steady Paws site."""

from __future__ import annotations

import logging
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
LOGGER = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]

# Data schema: files that define the minimum deployable product.
REQUIRED_FILES = (
    "index.html",
    "404.html",
    "styles/base.css",
    "styles/components.css",
    "assets/paw.svg",
    "downloads/diabetic-cat-tracker.pdf",
    "netlify.toml",
    "robots.txt",
    "sitemap.xml",
)
EXPECTED_SITE_URL = "https://steadypaws.netlify.app/"
EXPECTED_SUPPORT_URL = "https://buymeacoffee.com/divclass016"


class LinkParser(HTMLParser):
    """Collect href/src targets without adding third-party dependencies."""

    def __init__(self) -> None:
        super().__init__()
        self.targets: list[str] = []
        self.h1_count = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        try:
            values = dict(attrs)
            if tag == "h1":
                self.h1_count += 1
            for key in ("href", "src"):
                value = values.get(key)
                if value:
                    self.targets.append(value)
        except Exception as exc:
            LOGGER.exception("Failed while parsing HTML tag %s: %s", tag, exc)
            raise


def assert_required_files() -> None:
    try:
        missing = [path for path in REQUIRED_FILES if not (ROOT / path).is_file()]
        if missing:
            raise AssertionError(f"Missing required files: {', '.join(missing)}")
        LOGGER.info("Required production files: PASS")
    except Exception as exc:
        LOGGER.exception("Required file check failed: %s", exc)
        raise


def assert_homepage() -> None:
    try:
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        required_markers = (
            'lang="en"',
            'name="viewport"',
            'name="description"',
            'name="robots" content="index, follow"',
            f'rel="canonical" href="{EXPECTED_SITE_URL}"',
            f'property="og:url" content="{EXPECTED_SITE_URL}"',
            EXPECTED_SUPPORT_URL,
            "/downloads/diabetic-cat-tracker.pdf",
        )
        missing = [marker for marker in required_markers if marker not in html]
        if missing:
            raise AssertionError(f"Homepage markers missing: {missing}")
        if "buymeacoffee.com/yourname" in html:
            raise AssertionError("Placeholder Buy Me a Coffee URL is still present")

        parser = LinkParser()
        parser.feed(html)
        if parser.h1_count != 1:
            raise AssertionError(f"Expected exactly one h1, found {parser.h1_count}")

        for target in parser.targets:
            parsed = urlparse(target)
            if parsed.scheme or target.startswith("#"):
                continue
            clean = parsed.path.lstrip("/")
            if not clean:
                continue
            if not (ROOT / clean).exists():
                raise AssertionError(f"Broken local reference: {target}")
        LOGGER.info("Homepage metadata and local references: PASS")
    except Exception as exc:
        LOGGER.exception("Homepage validation failed: %s", exc)
        raise


def assert_search_files() -> None:
    try:
        robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
        sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
        expected_sitemap_url = f"{EXPECTED_SITE_URL}sitemap.xml"
        if f"Sitemap: {expected_sitemap_url}" not in robots:
            raise AssertionError("robots.txt does not advertise the production sitemap")
        if f"<loc>{EXPECTED_SITE_URL}</loc>" not in sitemap:
            raise AssertionError("sitemap.xml does not contain the production homepage URL")
        LOGGER.info("Canonical crawler files: PASS")
    except Exception as exc:
        LOGGER.exception("Search file validation failed: %s", exc)
        raise


def assert_pdf() -> None:
    try:
        pdf = ROOT / "downloads/diabetic-cat-tracker.pdf"
        if pdf.stat().st_size < 1000:
            raise AssertionError("Tracker PDF is unexpectedly small")
        if pdf.read_bytes()[:5] != b"%PDF-":
            raise AssertionError("Tracker download is not a valid PDF signature")
        LOGGER.info("Printable tracker PDF: PASS")
    except Exception as exc:
        LOGGER.exception("PDF validation failed: %s", exc)
        raise


def main() -> int:
    try:
        assert_required_files()
        assert_homepage()
        assert_search_files()
        assert_pdf()
        LOGGER.info("STEADY PAWS QUALITY GATE: PASS")
        return 0
    except Exception:
        LOGGER.error("STEADY PAWS QUALITY GATE: FAIL")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
