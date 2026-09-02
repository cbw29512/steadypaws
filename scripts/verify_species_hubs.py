"""Verify Steady Paws species SEO hubs without touching medical content."""

from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
LOGGER = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]
SITE_URL = "https://steadypaws.netlify.app"
HUBS = {
    "cat": ROOT / "pets/cat-health-trackers.html",
    "dog": ROOT / "pets/dog-health-trackers.html",
}


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []
        self.h1_count = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "h1":
            self.h1_count += 1
        href = values.get("href")
        if href:
            self.hrefs.append(href)


def verify_hub(animal: str, path: Path) -> None:
    try:
        html = path.read_text(encoding="utf-8")
        required = (
            f"Free {animal.title()} Health Trackers",
            f"your {animal}'s health",
            "For organizing care, not medical advice.",
            "Your veterinarian makes the medical decisions.",
            f'rel="canonical" href="{SITE_URL}/pets/{animal}-health-trackers.html"',
            'name="robots" content="index, follow, max-image-preview:large"',
        )
        missing = [marker for marker in required if marker not in html]
        if missing:
            raise AssertionError(f"{animal} hub missing markers: {missing}")

        parser = LinkParser()
        parser.feed(html)
        if parser.h1_count != 1:
            raise AssertionError(f"{animal} hub must contain exactly one h1")
        care_links = [href for href in parser.hrefs if href.startswith("/care/")]
        if len(care_links) < 10:
            raise AssertionError(f"{animal} hub has too few care links: {len(care_links)}")
        for href in care_links:
            target = ROOT / urlparse(href).path.lstrip("/")
            if not target.is_file():
                raise AssertionError(f"Broken care link on {animal} hub: {href}")
        LOGGER.info("%s health tracker hub: PASS", animal.title())
    except Exception:
        LOGGER.exception("%s health tracker hub: FAIL", animal.title())
        raise


def verify_sitemap() -> None:
    try:
        robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
        expected_sitemap = f"Sitemap: {SITE_URL}/species-sitemap.xml"
        if expected_sitemap not in robots:
            raise AssertionError("robots.txt does not advertise species sitemap")

        tree = ET.parse(ROOT / "species-sitemap.xml")
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = {node.text for node in tree.findall("s:url/s:loc", ns) if node.text}
        expected = {f"{SITE_URL}/pets/{animal}-health-trackers.html" for animal in HUBS}
        if urls != expected:
            raise AssertionError(f"Species sitemap mismatch: {sorted(urls)}")
        LOGGER.info("Species sitemap + robots discovery: PASS")
    except Exception:
        LOGGER.exception("Species sitemap verification: FAIL")
        raise


def main() -> int:
    try:
        for animal, path in HUBS.items():
            verify_hub(animal, path)
        verify_sitemap()
        LOGGER.info("STEADY PAWS SPECIES SEO HUB GATE: PASS")
        return 0
    except Exception:
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
