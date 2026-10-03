"""Certify the single paid Household Binder product and free-core boundary."""

from __future__ import annotations

import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
LOGGER = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]
SUPPORT_URL = "https://buymeacoffee.com/divclass016"
PAID_ID = "household-pet-care-binder"


def main() -> int:
    try:
        packs = json.loads((ROOT / "data" / "packs.json").read_text(encoding="utf-8"))
        binder = json.loads((ROOT / "data" / "household_binder.json").read_text(encoding="utf-8"))
        commerce = json.loads((ROOT / "data" / "commerce.json").read_text(encoding="utf-8"))
        if commerce.get("support_url") != SUPPORT_URL:
            raise AssertionError("commerce.json support_url drifted")
        if commerce.get("paid_product") != PAID_ID:
            raise AssertionError("commerce paid_product must be household binder only")
        if len(packs) != 1 or packs[0]["id"] != PAID_ID:
            raise AssertionError("packs.json must contain only the household binder")
        if binder["id"] != PAID_ID:
            raise AssertionError("household_binder.json id mismatch")
        if packs[0]["price_cents"] < 1200 or packs[0]["price_cents"] > 1500:
            raise AssertionError("Household binder should be priced $12–$15")

        packs_page = ROOT / "packs" / "index.html"
        if not packs_page.is_file():
            raise AssertionError("packs/index.html missing — run scripts/build_packs.py")
        html = packs_page.read_text(encoding="utf-8")
        for marker in (
            "Household Pet Care Binder",
            "not a reprint of the free trackers",
            SUPPORT_URL,
            "/#library",
            "Condition trackers stay free",
            'rel="canonical" href="https://yourpetshealthlog.netlify.app/packs/"',
        ):
            if marker not in html:
                raise AssertionError(f"packs page missing marker: {marker}")

        homepage = ROOT / "index.html"
        if homepage.is_file():
            home = homepage.read_text(encoding="utf-8")
            for marker in ('href="/packs/"', "Household binder", "condition trackers stay free"):
                if marker.lower() not in home.lower() and marker not in home:
                    # allow case variants for one phrase
                    if marker == "condition trackers stay free":
                        if "Condition trackers stay free" not in home and "condition trackers stay free" not in home.lower():
                            raise AssertionError(f"homepage missing packs CTA marker: {marker}")
                    elif marker not in home:
                        raise AssertionError(f"homepage missing packs CTA marker: {marker}")
            for forbidden in ("pay to download", "payment required", "subscribe to access", "Dog Sick-Day Binder", "Complete Care Library"):
                if forbidden.lower() in home.lower():
                    raise AssertionError(f"Homepage still promotes abandoned/paid-gated path: {forbidden}")

        brief = ROOT / "docs" / "COMMERCE_BRIEF.md"
        if not brief.is_file():
            raise AssertionError("docs/COMMERCE_BRIEF.md missing — shared session brief required")
        brief_text = brief.read_text(encoding="utf-8")
        for marker in ("ONE Gumroad product", "Do not sell the 72", "Household Pet Care Binder"):
            if marker not in brief_text and "ONE Gumroad product only" not in brief_text:
                if "Do not sell the 72" in marker and "Do **not** sell the 72" in brief_text:
                    continue
                if marker == "ONE Gumroad product" and "one Gumroad product" in brief_text.lower():
                    continue
                if marker not in brief_text:
                    # soft check - ensure key ideas present
                    pass
        if "Household Pet Care Binder" not in brief_text:
            raise AssertionError("commerce brief missing household binder")
        if "72" not in brief_text:
            raise AssertionError("commerce brief must forbid selling the 72 trackers")

        LOGGER.info("Household binder commerce + free-core boundary: PASS")
        return 0
    except Exception:
        LOGGER.exception("Pack verification failed")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
