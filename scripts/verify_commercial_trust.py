"""Commercial trust certification for Steady Paws public pages."""

from __future__ import annotations

import logging
from html.parser import HTMLParser
from pathlib import Path

from tracker_catalog import TRACKERS

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
LOGGER = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]
SUPPORT_URL = "https://buymeacoffee.com/divclass016"
TERMS_PATH = "/terms.html"


class BasicParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.h1 = 0
        self.hrefs: list[str] = []
        self.has_main = False
        self.has_skip = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        classes = set((values.get("class") or "").split())
        if tag == "h1":
            self.h1 += 1
        if tag == "main":
            self.has_main = True
        if tag == "a" and "skip-link" in classes:
            self.has_skip = True
        if tag == "a" and values.get("href"):
            self.hrefs.append(values["href"] or "")


def assert_terms_page() -> None:
    path = ROOT / "terms.html"
    html = path.read_text(encoding="utf-8")
    required = (
        '<html lang="en">', 'name="viewport"', '<main id="main"',
        "Organization, not diagnosis or treatment", "Not an emergency service",
        "does not diagnose disease", "contact a veterinarian or veterinary emergency service promptly",
        "Support is optional", SUPPORT_URL, '/privacy.html', '/accessibility.html',
        'rel="canonical" href="https://steadypaws.netlify.app/terms.html"',
    )
    missing = [marker for marker in required if marker not in html]
    if missing:
        raise AssertionError(f"Terms page missing markers: {missing}")
    parser = BasicParser()
    parser.feed(html)
    if parser.h1 != 1 or not parser.has_main or not parser.has_skip:
        raise AssertionError("Terms page semantic/accessibility structure is incomplete")
    LOGGER.info("Terms + medical-use boundary: PASS")


def assert_support_and_terms(path: Path, label: str, *, require_privacy: bool = True) -> None:
    html = path.read_text(encoding="utf-8")
    missing = []
    for marker in (SUPPORT_URL, TERMS_PATH):
        if marker not in html:
            missing.append(marker)
    if require_privacy and "/privacy.html" not in html:
        missing.append("/privacy.html")
    if missing:
        raise AssertionError(f"{label} missing commercial trust links: {missing}")


def assert_public_coverage() -> None:
    assert_support_and_terms(ROOT / "index.html", "homepage")
    assert_support_and_terms(ROOT / "privacy.html", "privacy", require_privacy=False)
    assert_support_and_terms(ROOT / "accessibility.html", "accessibility")
    for animal in ("cat", "dog"):
        assert_support_and_terms(ROOT / "pets" / f"{animal}-health-trackers.html", f"{animal} hub")

    care_pages = sorted((ROOT / "care").glob("*.html"))
    if len(care_pages) != len(TRACKERS):
        raise AssertionError(f"Expected {len(TRACKERS)} care pages, found {len(care_pages)}")
    for path in care_pages:
        html = path.read_text(encoding="utf-8")
        for marker in (SUPPORT_URL, TERMS_PATH, "/privacy.html", "/accessibility.html", "For organizing care, not medical advice."):
            if marker not in html:
                raise AssertionError(f"{path.name} missing marker: {marker}")
    LOGGER.info("Homepage + 72 care pages + species/info pages carry trust/support links: PASS")


def assert_support_remains_optional() -> None:
    homepage = (ROOT / "index.html").read_text(encoding="utf-8")
    terms = (ROOT / "terms.html").read_text(encoding="utf-8")
    for forbidden in ("pay to download", "payment required", "subscribe to access"):
        if forbidden in homepage.lower() or forbidden in terms.lower():
            raise AssertionError(f"Support became access-gated: {forbidden}")
    if "No account. No email." not in homepage or "no account wall or paywall" not in homepage:
        raise AssertionError("Homepage free-access promise disappeared")
    LOGGER.info("Optional support / no-paywall boundary: PASS")


def main() -> int:
    try:
        assert_terms_page()
        assert_public_coverage()
        assert_support_remains_optional()
        LOGGER.info("STEADY PAWS COMMERCIAL TRUST GATE: PASS")
        return 0
    except Exception:
        LOGGER.exception("STEADY PAWS COMMERCIAL TRUST GATE: FAIL")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
