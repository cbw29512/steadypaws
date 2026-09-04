"""Apply deterministic commercial trust links after Steady Paws static generation."""

from __future__ import annotations

import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
LOGGER = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]
SUPPORT_URL = "https://buymeacoffee.com/divclass016"

CARE_FOOTER = (
    '<footer class="care-footer"><p>Steady Paws · Free pet health trackers for animals you love · '
    '<a href="/accessibility.html">Accessibility options</a> · <a href="/privacy.html">Privacy</a> · '
    '<a href="/terms.html">Terms</a> · '
    f'<a href="{SUPPORT_URL}" target="_blank" rel="noopener noreferrer">Support Steady Paws</a></p></footer>'
)


def append_footer_links(path: Path) -> None:
    html = path.read_text(encoding="utf-8")
    closing = "</div></div></footer>"
    if closing not in html:
        raise ValueError(f"Footer marker missing: {path}")
    terms_link = '<a href="/terms.html">Terms</a>'
    support_link = f'<a href="{SUPPORT_URL}" target="_blank" rel="noopener noreferrer">Support Steady Paws</a>'
    additions = ""
    if terms_link not in html:
        additions += terms_link
    if SUPPORT_URL not in html:
        additions += support_link
    if additions:
        html = html.replace(closing, additions + closing, 1)
    path.write_text(html, encoding="utf-8")


def polish_care_pages() -> int:
    count = 0
    for path in sorted((ROOT / "care").glob("*.html")):
        html = path.read_text(encoding="utf-8")
        start = html.find('<footer class="care-footer">')
        if start < 0:
            raise ValueError(f"Care footer missing: {path.name}")
        end = html.find("</footer>", start)
        if end < 0:
            raise ValueError(f"Care footer is not closed: {path.name}")
        end += len("</footer>")
        html = html[:start] + CARE_FOOTER + html[end:]
        path.write_text(html, encoding="utf-8")
        count += 1
    return count


def main() -> int:
    try:
        for path in (
            ROOT / "index.html",
            ROOT / "pets" / "cat-health-trackers.html",
            ROOT / "pets" / "dog-health-trackers.html",
            ROOT / "privacy.html",
            ROOT / "accessibility.html",
        ):
            append_footer_links(path)
        care_count = polish_care_pages()
        LOGGER.info("Commercial trust polish applied to homepage, %d care pages, hubs, and information pages", care_count)
        return 0
    except Exception:
        LOGGER.exception("Commercial trust polish failed")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
