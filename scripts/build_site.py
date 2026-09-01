"""Build the static homepage from the shared tracker catalog."""

from __future__ import annotations

from collections import Counter
from html import escape
from pathlib import Path

from tracker_catalog import CONDITION_NAMES, GROUP_LABELS, TRACKERS, condition_key, condition_name

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "templates" / "index.template.html"
OUTPUT = ROOT / "index.html"
ASSET_REV = "20260901-pawphoto1"


def grouped_conditions() -> list[tuple[str, list[dict]]]:
    grouped: dict[str, list[dict]] = {}
    for item in TRACKERS:
        grouped.setdefault(condition_name(item), []).append(item)
    return sorted(grouped.items(), key=lambda pair: pair[0].casefold())


def group_counts() -> Counter:
    counts: Counter = Counter()
    for _, variants in grouped_conditions():
        for group in {item["group"] for item in variants}:
            counts[group] += 1
    return counts


def render_filters() -> str:
    counts = group_counts()
    parts = [
        f'<button class="filter-chip is-active" type="button" data-filter="all" aria-pressed="true">All <span>{len(CONDITION_NAMES)}</span></button>'
    ]
    for key in ("cat", "dog", "small-mammal", "bird", "reptile", "horse", "aquatic", "universal"):
        parts.append(
            f'<button class="filter-chip" type="button" data-filter="{key}" aria-pressed="false">'
            f'{escape(GROUP_LABELS[key])} <span>{counts[key]}</span></button>'
        )
    return "\n            ".join(parts)


def badge_class(group: str) -> str:
    return group.replace("-", "_")


def badge_label(item: dict) -> str:
    species = item["species"].strip()
    if item["group"] == "universal" or species.lower() in {"all pets", "all"}:
        return "For any family member"
    return f"For {species.lower()}"


def care_page(item: dict) -> str:
    return f'/care/{Path(item["filename"]).stem}.html'


def render_variant(item: dict, concern: str) -> str:
    search = escape(f'{item["species"]} {item["search"]} {item["description"]}', quote=True)
    filename = escape(item["filename"], quote=True)
    species = item["species"].strip()
    download_label = escape(f"Download {concern} printable care paperwork for {species}", quote=True)
    accessible_label = escape(f"Open accessible {concern} web worksheet for {species}", quote=True)
    return (
        f'<div class="tracker-variant" data-group="{escape(item["group"], quote=True)}" '
        f'data-species="{escape(species, quote=True)}" data-search="{search}">'
        f'<span class="species-badge {badge_class(item["group"])}">{escape(badge_label(item))}</span>'
        f'<p>{escape(item["description"])}</p>'
        f'<a class="download-link care-download" href="/downloads/{filename}" aria-label="{download_label}" '
        f'data-pdf-url="/downloads/{filename}" data-download-name="{filename}" download>'
        f'Get their care paperwork <span aria-hidden="true">↓</span></a>'
        f'<a class="accessible-link" href="{care_page(item)}" aria-label="{accessible_label}">Accessible web worksheet</a>'
        f'</div>'
    )


def render_cards() -> str:
    cards = []
    for name, variants in grouped_conditions():
        key = condition_key(variants[0])
        search = escape(
            " ".join([name] + [f'{item["species"]} {item["search"]}' for item in variants]),
            quote=True,
        )
        rendered_variants = "".join(render_variant(item, name) for item in variants)
        cards.append(
            f'<article class="tracker-card condition-card" data-condition="{escape(key, quote=True)}" '
            f'data-search="{search}">'
            f'<span class="condition-kicker">Primary health concern</span>'
            f'<h3>{escape(name)}</h3>'
            f'<p class="condition-help">Choose the version made for your family member. The form also has room to note other conditions they are living with.</p>'
            f'<div class="tracker-variants">{rendered_variants}</div></article>'
        )
    return "\n          ".join(cards)


def main() -> int:
    template = TEMPLATE.read_text(encoding="utf-8")
    html = (
        template.replace("{{TOTAL}}", str(len(TRACKERS)))
        .replace("{{CONDITION_TOTAL}}", str(len(CONDITION_NAMES)))
        .replace("{{FILTERS}}", render_filters())
        .replace("{{TRACKER_CARDS}}", render_cards())
        .replace('href="/styles/base.css"', f'href="/styles/base.css?v={ASSET_REV}"')
        .replace('href="/styles/components.css"', f'href="/styles/components.css?v={ASSET_REV}"')
        .replace('href="/assets/paw.svg"', f'href="/assets/paw.svg?v={ASSET_REV}"')
        .replace('src="/assets/paw.svg"', f'src="/assets/paw.svg?v={ASSET_REV}"')
        .replace('src="/assets/site.js"', f'src="/assets/site.js?v={ASSET_REV}"')
        .replace(
            "</head>",
            '<script src="/assets/personalization-bridge-print1.js" defer></script>\n'
            f'  <link rel="stylesheet" href="/styles/family.css?v={ASSET_REV}">\n</head>',
        )
    )
    if "{{" in html or "}}" in html:
        raise RuntimeError("Unresolved homepage template placeholder")
    OUTPUT.write_text(html, encoding="utf-8")
    print(
        f"Built {OUTPUT} with {len(CONDITION_NAMES)} unique health concerns, "
        f"{len(TRACKERS)} tailored care forms, asset revision {ASSET_REV}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
