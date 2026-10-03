"""Build the public packs marketing page for the ONE paid Gumroad product.

Paid product: Household Pet Care Binder & Sitter Handover.
Does not sell the free 72 condition trackers. Fulfillment PDFs come from
scripts/build_household_binder.py (local only).
"""

from __future__ import annotations

import json
import logging
from html import escape
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
LOGGER = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
PACKS_DIR = ROOT / "packs"
TEMPLATE = ROOT / "templates" / "packs.template.html"
COMMERCE_PATH = ROOT / "data" / "commerce.json"
PACKS_PATH = ROOT / "data" / "packs.json"
BINDER_PATH = ROOT / "data" / "household_binder.json"
ASSET_REV = "20261003-convert1"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def render_pack_cards(packs: list[dict], support_url: str, binder: dict) -> str:
    cards = []
    for pack in packs:
        checkout = pack.get("checkout_url") or binder.get("checkout_url")
        diffs = "".join(f"<li>{escape(item)}</li>" for item in binder.get("differentiators", []))
        if checkout:
            action = (
                f'<a class="button" href="{escape(checkout)}" target="_blank" rel="noopener noreferrer">'
                f'Buy binder · {escape(pack["price_display"])}</a>'
            )
            note = (
                "<p class=\"pack-note\">Checkout opens in a new tab. "
                "The 72 condition trackers and Quick Phone Log stay free on this site.</p>"
            )
        else:
            action = (
                f'<a class="button button-coffee" href="{escape(support_url)}" target="_blank" rel="noopener noreferrer">'
                f'<span aria-hidden="true">☕</span> Tip jar while checkout is prepared</a>'
            )
            note = (
                "<p class=\"pack-note\">Paid checkout is not live yet. "
                "When it is, this button becomes the Gumroad purchase link. "
                "Condition trackers stay free.</p>"
            )
        cards.append(
            f'<article class="pack-card" id="{escape(pack["id"])}">'
            f'<p class="card-kicker">{escape(pack["eyebrow"])}</p>'
            f'<h2>{escape(pack["title"])}</h2>'
            f'<p class="pack-price">{escape(pack["price_display"])}</p>'
            f'<p>{escape(pack["blurb"])}</p>'
            f'<p class="pack-audience"><strong>For:</strong> {escape(pack["audience"])}</p>'
            f'<ul class="pack-includes">{diffs}</ul>'
            f'<div class="pack-actions">{action}'
            f'<a class="button button-secondary" href="/#library">Browse free trackers</a></div>'
            f"{note}</article>"
        )
    return "\n".join(cards)


def build_packs_page(packs: list[dict], commerce: dict, binder: dict) -> Path:
    support_url = commerce["support_url"]
    welcome_url = commerce.get("welcome_url", "https://welcomehomepet.netlify.app/")
    html = TEMPLATE.read_text(encoding="utf-8")
    html = (
        html.replace("{{PACK_CARDS}}", render_pack_cards(packs, support_url, binder))
        .replace("{{SUPPORT_URL}}", escape(support_url))
        .replace("{{WELCOME_URL}}", escape(welcome_url))
        .replace("{{ASSET_REV}}", ASSET_REV)
        .replace("{{PACK_COUNT}}", str(len(packs)))
    )
    PACKS_DIR.mkdir(parents=True, exist_ok=True)
    out = PACKS_DIR / "index.html"
    out.write_text(html, encoding="utf-8")
    LOGGER.info("Wrote %s", out.relative_to(ROOT))
    return out


def main() -> int:
    try:
        commerce = load_json(COMMERCE_PATH)
        packs = load_json(PACKS_PATH)
        binder = load_json(BINDER_PATH)
        if not packs:
            raise ValueError("No packs defined")
        if packs[0]["id"] != "household-pet-care-binder":
            raise ValueError("Paid product must be household-pet-care-binder only")
        build_packs_page(packs, commerce, binder)
        live = 1 if (packs[0].get("checkout_url") or binder.get("checkout_url")) else 0
        LOGGER.info("Packs page ready: household binder only, checkout live=%s", bool(live))
        return 0
    except Exception:
        LOGGER.exception("Pack page build failed")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
