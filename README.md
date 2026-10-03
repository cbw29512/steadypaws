# Your Pet’s Health Log

Your Pet’s Health Log is a privacy-conscious library of free printable **care paperwork for someone you love**. The experience starts with the family member being cared for, then guides the person to the health problem or care challenge they are going through and the right printable tracker.

## Current production library

The shared catalog contains **72 two-page printable tools** across:

- Cats — 10
- Dogs — 10
- Small & furry family members — 26 (rabbits, guinea pigs, ferrets, chinchillas, hamsters, rats and mice)
- Birds — 6
- Reptiles — 6
- Horses — 6
- Aquarium fish and amphibians — 6
- Any-pet care tools — 2

The forms are organizational aids. They do not diagnose disease, prescribe medication, or establish species-specific medical or husbandry targets. Those decisions belong with an appropriate veterinarian or qualified animal-health professional.

## Family-first UX

The default journey is:

1. **Who are we caring for today?**
2. **What tough time are they going through?**
3. **Get their tracker.**

The complete searchable library remains available, but it is secondary to this guided path. User-facing cards avoid unnecessary clinical species prefixes, while condition names and observation fields remain precise where medical accuracy matters.

The generated PDFs use warmer labels such as **Their name**, **How they did this week**, **What changed since their last visit**, and **Questions for their veterinary team**.

## Architecture

`data/trackers/*.json` is the source of truth for the tracker library. `scripts/tracker_catalog.py` loads the catalog. `scripts/build_trackers.py` generates every PDF. `scripts/build_site.py` generates the family-first searchable homepage from the same catalog. `scripts/verify_site.py` certifies the catalog, guided picker, homepage links, crawler files, PDF signatures, and exact two-page count.

This keeps the displayed download count, family choices, search cards, generated files, and CI requirements synchronized as the library grows.

## Local production check

```bash
python -m pip install -r requirements.txt
python scripts/build_trackers.py
python scripts/build_site.py
python scripts/build_packs.py
python scripts/build_household_binder.py
python scripts/verify_site.py
python scripts/verify_packs.py
```

**Commerce rule (see `docs/COMMERCE_BRIEF.md`):** the site stays the free app (72 condition trackers + Quick Phone Log). Gumroad sells **one** product — the Household Pet Care Binder & Sitter Handover ($12–$15). Do not sell reprints of the free trackers.

`scripts/build_packs.py` writes the public `/packs/` marketing page.  
`scripts/build_household_binder.py` writes fillable US Letter + A4 PDFs under `fulfillment/household-binder/` for Gumroad upload (gitignored; never published by Netlify).

Set `checkout_url` in `data/household_binder.json` / `data/packs.json` only when Gumroad is live. **Do not publish site buy-button changes before that URL exists.**

## Netlify

Netlify reads `netlify.toml` and runs the tracker generator, homepage builder, and packs page builder before publishing the repository root. The production URL is `https://yourpetshealthlog.netlify.app/`. Only production context builds (credit protection).

## Product principles

- Family member first, condition second
- No account or email wall
- No health-log collection in the current version
- Mobile-first, keyboard-accessible static UI
- Lightweight HTML/CSS/JavaScript
- Printable Letter-size PDF resources
- Species-specific observation fields where physiology or husbandry differs
- Clear boundary between organization and veterinary medical advice

## Download and support paths

Every surface that can hand someone a tracker leads with the download, and offers
optional support next to that action rather than buried below it:

- **Homepage** — the whole library renders on load; the pet picker, filter chips
  and search narrow it. A persistent support note sits above the grid, and after
  a download the support card moves inline under the tracker that was taken.
- **Species hubs** (`pets/*.html`) — each concern offers a direct PDF download
  beside its online worksheet, with the same support note above the grid.
- **Care worksheets** (`care/*.html`) — a download/print finish block with a
  support slot beside it, both hidden in print.
- **Quick Phone Log** (`app/`) — optional support after a vet summary is
  prepared, hidden in print so the clinical record stays clean.
- **Printable PDFs** — every page footer carries the site host and the support
  host, because a printed sheet has no other way back.

The site support link points to `https://buymeacoffee.com/divclass016`.

`scripts/build_og_card.py` renders the shared social preview card. It is run by
hand and the PNG is committed, so deploys never depend on host fonts.
