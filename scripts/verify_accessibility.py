"""Static WCAG-oriented accessibility checks for every Steady Paws HTML page."""

from __future__ import annotations

import logging
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
LOGGER = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]


class AccessibilityParser(HTMLParser):
    def __init__(self, source: Path) -> None:
        super().__init__()
        self.source = source
        self.lang: str | None = None
        self.viewport = False
        self.main_count = 0
        self.h1_count = 0
        self.headings: list[int] = []
        self.ids: list[str] = []
        self.label_for: set[str] = set()
        self.label_depth = 0
        self.controls: list[tuple[str, dict[str, str | None], bool]] = []
        self.images: list[dict[str, str | None]] = []
        self.blank_links: list[dict[str, str | None]] = []
        self.positive_tabindex: list[str] = []
        self.inline_styles = 0
        self.inline_scripts = 0
        self.title_depth = 0
        self.title_text = ""
        self.meta_description: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "html":
            self.lang = values.get("lang")
        if tag == "meta" and values.get("name") == "viewport":
            self.viewport = True
        if tag == "meta" and values.get("name") == "description":
            self.meta_description = values.get("content")
        if tag == "main":
            self.main_count += 1
        if tag == "title":
            self.title_depth += 1
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            level = int(tag[1])
            self.headings.append(level)
            if level == 1:
                self.h1_count += 1
        element_id = values.get("id")
        if element_id:
            self.ids.append(element_id)
        if tag == "label":
            self.label_depth += 1
            target = values.get("for")
            if target:
                self.label_for.add(target)
        if tag in {"input", "textarea", "select"}:
            if values.get("type") != "hidden":
                self.controls.append((tag, values, self.label_depth > 0))
        if tag == "img":
            self.images.append(values)
        if tag == "a" and values.get("target") == "_blank":
            self.blank_links.append(values)
        tabindex = values.get("tabindex")
        if tabindex and re.fullmatch(r"[1-9]\d*", tabindex):
            self.positive_tabindex.append(f"{tag}#{element_id or ''}[tabindex={tabindex}]")
        if "style" in values:
            self.inline_styles += 1
        if tag == "script" and not values.get("src"):
            self.inline_scripts += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "label" and self.label_depth:
            self.label_depth -= 1
        if tag == "title" and self.title_depth:
            self.title_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.title_depth:
            self.title_text += data


def accessible_control_name(values: dict[str, str | None], nested_label: bool, label_for: set[str]) -> bool:
    if nested_label:
        return True
    if values.get("aria-label") or values.get("aria-labelledby"):
        return True
    element_id = values.get("id")
    return bool(element_id and element_id in label_for)


def assert_html_page(path: Path) -> None:
    parser = AccessibilityParser(path)
    parser.feed(path.read_text(encoding="utf-8"))

    if parser.lang != "en":
        raise AssertionError(f"{path}: expected html lang=en")
    if not parser.viewport:
        raise AssertionError(f"{path}: missing viewport metadata")
    if parser.main_count != 1:
        raise AssertionError(f"{path}: expected exactly one main landmark, found {parser.main_count}")
    if parser.h1_count != 1:
        raise AssertionError(f"{path}: expected exactly one h1, found {parser.h1_count}")
    if not parser.title_text.strip() or len(parser.title_text.strip()) > 70:
        raise AssertionError(f"{path}: title missing or longer than 70 characters")
    if path.name != "404.html" and (not parser.meta_description or not 50 <= len(parser.meta_description) <= 180):
        raise AssertionError(f"{path}: meta description missing or outside 50-180 characters")
    if len(parser.ids) != len(set(parser.ids)):
        raise AssertionError(f"{path}: duplicate element ids")
    for previous, current in zip(parser.headings, parser.headings[1:]):
        if current > previous + 1:
            raise AssertionError(f"{path}: heading level jumps from h{previous} to h{current}")
    if parser.inline_styles:
        raise AssertionError(f"{path}: contains {parser.inline_styles} inline style attributes")
    if parser.inline_scripts:
        raise AssertionError(f"{path}: contains inline JavaScript")
    if parser.positive_tabindex:
        raise AssertionError(f"{path}: positive tabindex found: {parser.positive_tabindex}")
    for attrs in parser.images:
        if "alt" not in attrs:
            raise AssertionError(f"{path}: image missing alt attribute")
    for tag, attrs, nested in parser.controls:
        if not accessible_control_name(attrs, nested, parser.label_for):
            raise AssertionError(f"{path}: {tag} lacks an accessible label: {attrs}")
    for attrs in parser.blank_links:
        rel = set((attrs.get("rel") or "").lower().split())
        if "noopener" not in rel:
            raise AssertionError(f"{path}: target=_blank link missing rel=noopener")


def luminance(hex_color: str) -> float:
    color = hex_color.lstrip("#")
    channels = [int(color[index:index + 2], 16) / 255 for index in (0, 2, 4)]
    converted = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in channels]
    return 0.2126 * converted[0] + 0.7152 * converted[1] + 0.0722 * converted[2]


def contrast(foreground: str, background: str) -> float:
    lighter, darker = sorted((luminance(foreground), luminance(background)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def require_contrast(label: str, foreground: str, background: str, minimum: float) -> None:
    ratio = contrast(foreground, background)
    if ratio + 1e-9 < minimum:
        raise AssertionError(f"{label}: contrast {ratio:.2f}:1 is below {minimum:.1f}:1")
    LOGGER.info("Contrast %-28s %.2f:1", label, ratio)


def assert_wcag_palette() -> None:
    pairs = (
        ("body muted on cream", "#62716c", "#fffdf9", 4.5),
        ("body muted on soft", "#62716c", "#f3f7f5", 4.5),
        ("body muted on sand", "#62716c", "#faf6f0", 4.5),
        ("eyebrow on cream", "#5a7169", "#fffdf9", 4.5),
        ("eyebrow on soft", "#5a7169", "#f3f7f5", 4.5),
        ("eyebrow on safety", "#5a7169", "#fbf3e9", 4.5),
        ("primary button", "#fffefa", "#55756c", 4.5),
        ("button hover", "#fffefa", "#5f776f", 4.5),
        ("heart strip copy", "#7b6a5f", "#fbf2eb", 4.5),
        ("photo placeholder", "#806f64", "#fffefa", 4.5),
        ("active chip count", "#587168", "#eaf2ef", 4.5),
        ("reptile badge", "#60704f", "#eff3e7", 4.5),
        ("focus indicator", "#976a40", "#fffdf9", 3.0),
        ("control boundary", "#82978f", "#fffefa", 3.0),
        ("alternate family boundary", "#9d897a", "#fffefa", 3.0),
    )
    for values in pairs:
        require_contrast(*values)

    base = (ROOT / "styles/base.css").read_text(encoding="utf-8")
    components = (ROOT / "styles/components.css").read_text(encoding="utf-8")
    family = (ROOT / "styles/family.css").read_text(encoding="utf-8")
    care = (ROOT / "styles/care.css").read_text(encoding="utf-8")
    required_markers = (
        (base, "--muted: #62716c;"),
        (base, "--brand-2: #5a7169;"),
        (base, "--focus: #976a40;"),
        (base, ":where(a,button,input,textarea,summary):focus-visible"),
        (base, "@media (prefers-reduced-motion: reduce)"),
        (base, ".brand-logo {"),
        (components, "border:1px solid #82978f"),
        (components, '.photo-field input[type="file"]'),
        (components, "::file-selector-button"),
        (family, "border:1px solid #9d897a"),
        (care, ".care-table th"),
        (care, "border:1px solid #82978f"),
    )
    for text, marker in required_markers:
        if marker not in text:
            raise AssertionError(f"Required accessibility CSS marker missing: {marker}")
    LOGGER.info("WCAG-oriented palette, visible photo control, focus, boundaries, reduced motion: PASS")


def assert_all_html() -> None:
    pages = [ROOT / "index.html", ROOT / "404.html", ROOT / "accessibility.html", ROOT / "privacy.html"]
    pages.extend(sorted((ROOT / "care").glob("*.html")))
    if len(pages) != 76:
        raise AssertionError(f"Expected 76 audited HTML pages, found {len(pages)}")
    for page in pages:
        assert_html_page(page)
    LOGGER.info("Semantic HTML audit across all 76 pages: PASS")


def assert_no_external_runtime_dependencies() -> None:
    html_pages = [ROOT / "index.html", ROOT / "404.html", ROOT / "accessibility.html", ROOT / "privacy.html"]
    html_pages.extend((ROOT / "care").glob("*.html"))
    allowed_external_hosts = {"steadypaws.netlify.app", "buymeacoffee.com", "schema.org"}
    for path in html_pages:
        text = path.read_text(encoding="utf-8")
        for url in re.findall(r'https://[^"\'<>\s]+', text):
            host = urlparse(url).hostname
            if host and host not in allowed_external_hosts:
                raise AssertionError(f"Unexpected external runtime/resource host in {path}: {host}")
    LOGGER.info("No third-party runtime scripts/styles/fonts/trackers: PASS")


def main() -> int:
    try:
        assert_all_html()
        assert_wcag_palette()
        assert_no_external_runtime_dependencies()
        LOGGER.info("STEADY PAWS WCAG 2.2 AA STATIC GATE: PASS")
        return 0
    except Exception as exc:
        LOGGER.exception("STEADY PAWS WCAG 2.2 AA STATIC GATE: FAIL: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
