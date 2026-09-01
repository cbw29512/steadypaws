"""Build the static homepage from the shared tracker catalog."""

from __future__ import annotations

from collections import Counter
from html import escape
from pathlib import Path

from tracker_catalog import GROUP_LABELS, TRACKERS

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "templates" / "index.template.html"
OUTPUT = ROOT / "index.html"


def group_counts() -> Counter:
    return Counter(item["group"] for item in TRACKERS)


def render_filters() -> str:
    counts = group_counts()
    parts = [
        f'<button class="filter-chip is-active" type="button" data-filter="all" aria-pressed="true">All <span>{len(TRACKERS)}</span></button>'
    ]
    for key in ("cat", "dog", "small-mammal", "bird", "reptile", "horse", "aquatic", "universal"):
        parts.append(
            f'<button class="filter-chip" type="button" data-filter="{key}" aria-pressed="false">'
            f'{escape(GROUP_LABELS[key])} <span>{counts[key]}</span></button>'
        )
    return "\n            ".join(parts)


def badge_class(group: str) -> str:
    return group.replace("-", "_")


def friendly_title(item: dict) -> str:
    """Remove clinical species prefixes from the user-facing card title."""
    title = item["title"].strip()
    prefixes = (
        f'{item["species"]} ',
        "Feline ",
        "Canine ",
        "Equine ",
        "Avian ",
    )
    for prefix in prefixes:
        if title.lower().startswith(prefix.lower()):
            title = title[len(prefix):]
            break
    if title.endswith(" Tracker"):
        title = title[:-8]
    return title.strip()


def badge_label(item: dict) -> str:
    species = item["species"].strip()
    if item["group"] == "universal" or species.lower() in {"all pets", "all"}:
        return "For any pet"
    return f"For {species.lower()}"


def render_cards() -> str:
    cards = []
    for item in TRACKERS:
        search = escape(f'{item["species"]} {item["search"]}', quote=True)
        cards.append(
            f'<article class="tracker-card" data-group="{escape(item["group"], quote=True)}" '
            f'data-species="{escape(item["species"], quote=True)}" data-search="{search}">'
            f'<span class="species-badge {badge_class(item["group"])}">{escape(badge_label(item))}</span>'
            f'<h3>{escape(friendly_title(item))}</h3><p>{escape(item["description"])}</p>'
            f'<a class="download-link" href="/downloads/{escape(item["filename"], quote=True)}" download>'
            f'Get their tracker <span aria-hidden="true">↓</span></a></article>'
        )
    return "\n          ".join(cards)


def main() -> int:
    template = TEMPLATE.read_text(encoding="utf-8")
    html = (
        template.replace("{{TOTAL}}", str(len(TRACKERS)))
        .replace("{{FILTERS}}", render_filters())
        .replace("{{TRACKER_CARDS}}", render_cards())
    )
    if "{{" in html or "}}" in html:
        raise RuntimeError("Unresolved homepage template placeholder")
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"Built {OUTPUT} with {len(TRACKERS)} tracker cards")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
