# Steady Paws

Steady Paws is a privacy-conscious library of free printable **care paperwork for someone you love**. The experience starts with the family member being cared for, then guides the person to the health problem or care challenge they are going through and the right printable tracker.

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
python scripts/verify_site.py
```

## Netlify

Netlify reads `netlify.toml` and runs the tracker generator and homepage builder before publishing the repository root. The production URL is `https://steadypaws.netlify.app/`.

## Product principles

- Family member first, condition second
- No account or email wall
- No health-log collection in the current version
- Mobile-first, keyboard-accessible static UI
- Lightweight HTML/CSS/JavaScript
- Printable Letter-size PDF resources
- Species-specific observation fields where physiology or husbandry differs
- Clear boundary between organization and veterinary medical advice

## Support

The site support link points to `https://buymeacoffee.com/divclass016`.
