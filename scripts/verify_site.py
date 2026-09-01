"""Static production checks for the Steady Paws site."""
from __future__ import annotations
import logging
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
LOGGER = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SITE_URL = "https://steadypaws.netlify.app/"
EXPECTED_SUPPORT_URL = "https://buymeacoffee.com/divclass016"
TRACKERS = (
    "diabetic-cat-tracker.pdf", "ckd-cat-tracker.pdf", "hyperthyroid-cat-tracker.pdf", "feline-asthma-tracker.pdf",
    "cat-arthritis-mobility-tracker.pdf", "cat-heart-disease-tracker.pdf", "cat-hypertension-tracker.pdf", "cat-chronic-gi-ibd-tracker.pdf", "cat-seizure-tracker.pdf", "cat-cancer-supportive-care-tracker.pdf",
    "dog-diabetes-tracker.pdf", "dog-ckd-tracker.pdf", "dog-arthritis-mobility-tracker.pdf", "dog-heart-disease-tracker.pdf", "dog-cushings-tracker.pdf", "dog-hypothyroidism-tracker.pdf", "dog-seizure-epilepsy-tracker.pdf", "dog-allergy-skin-tracker.pdf", "dog-chronic-gi-tracker.pdf", "dog-cancer-supportive-care-tracker.pdf",
    "universal-medication-appointment-planner.pdf", "universal-quality-of-life-tracker.pdf",
)
REQUIRED_FILES = (
    "index.html", "404.html", "styles/base.css", "styles/components.css", "assets/paw.svg", "assets/site.js",
    "netlify.toml", "robots.txt", "sitemap.xml", "requirements.txt", "scripts/build_trackers.py",
    *tuple(f"downloads/{name}" for name in TRACKERS),
)

class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(); self.targets=[]; self.h1_count=0; self.downloads=[]
    def handle_starttag(self, tag, attrs):
        values=dict(attrs)
        if tag == "h1": self.h1_count += 1
        href=values.get("href"); src=values.get("src")
        if href: self.targets.append(href)
        if src: self.targets.append(src)
        if tag == "a" and href and href.startswith("/downloads/"): self.downloads.append(href)

def assert_required_files():
    missing=[path for path in REQUIRED_FILES if not (ROOT/path).is_file()]
    if missing: raise AssertionError(f"Missing required files: {', '.join(missing)}")
    LOGGER.info("Required production files: PASS")

def assert_homepage():
    html=(ROOT/"index.html").read_text(encoding="utf-8")
    markers=('lang="en"','name="viewport"','name="description"','name="robots" content="index, follow"',f'rel="canonical" href="{EXPECTED_SITE_URL}"',EXPECTED_SUPPORT_URL,'Browse 22 free trackers')
    missing=[marker for marker in markers if marker not in html]
    if missing: raise AssertionError(f"Homepage markers missing: {missing}")
    if "In development" in html: raise AssertionError("Production homepage still contains an In development tracker")
    parser=LinkParser(); parser.feed(html)
    if parser.h1_count != 1: raise AssertionError(f"Expected one h1, found {parser.h1_count}")
    expected={f"/downloads/{name}" for name in TRACKERS}
    if set(parser.downloads) != expected: raise AssertionError(f"Download link mismatch: expected {len(expected)}, found {len(set(parser.downloads))}")
    for target in parser.targets:
        parsed=urlparse(target)
        if parsed.scheme or target.startswith("#"): continue
        clean=parsed.path.lstrip("/")
        if clean and not (ROOT/clean).exists(): raise AssertionError(f"Broken local reference: {target}")
    LOGGER.info("Homepage metadata and 22 download links: PASS")

def assert_search_files():
    robots=(ROOT/"robots.txt").read_text(encoding="utf-8"); sitemap=(ROOT/"sitemap.xml").read_text(encoding="utf-8")
    if f"Sitemap: {EXPECTED_SITE_URL}sitemap.xml" not in robots: raise AssertionError("robots.txt missing production sitemap")
    if f"<loc>{EXPECTED_SITE_URL}</loc>" not in sitemap: raise AssertionError("sitemap missing production homepage")
    LOGGER.info("Crawler files: PASS")

def assert_pdfs():
    bad=[]
    for name in TRACKERS:
        data=(ROOT/"downloads"/name).read_bytes()
        if len(data) < 3000 or data[:5] != b"%PDF-" or b"/Count 2" not in data: bad.append(name)
    if bad: raise AssertionError(f"Invalid two-page tracker PDFs: {bad}")
    LOGGER.info("22 generated two-page tracker PDFs: PASS")

def main():
    try:
        assert_required_files(); assert_homepage(); assert_search_files(); assert_pdfs(); LOGGER.info("STEADY PAWS QUALITY GATE: PASS"); return 0
    except Exception as exc:
        LOGGER.exception("STEADY PAWS QUALITY GATE: FAIL: %s", exc); return 1

if __name__ == "__main__": raise SystemExit(main())
