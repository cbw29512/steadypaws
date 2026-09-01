# Steady Paws

Steady Paws is a privacy-conscious static resource library of free printable chronic-care and veterinary observation trackers for companion animals.

## Current production library

The shared catalog contains **72 two-page printable tools** across:

- Cats — 10
- Dogs — 10
- Small mammals — 26 (rabbits, guinea pigs, ferrets, chinchillas, hamsters, rats and mice)
- Birds — 6
- Reptiles — 6
- Horses — 6
- Aquarium fish and amphibians — 6
- Universal pet-care tools — 2

The forms are organizational aids. They do not diagnose disease, prescribe medication, or establish species-specific medical/husbandry targets. Those decisions belong with an appropriate veterinarian or qualified animal-health professional.

## Architecture

`data/trackers/*.json` is the source of truth for the tracker library. `scripts/tracker_catalog.py` loads the catalog. `scripts/build_trackers.py` generates every PDF. `scripts/build_site.py` generates the searchable homepage from the same catalog. `scripts/verify_site.py` certifies the catalog, homepage links, crawler files, PDF signatures, and exact two-page count.

This keeps the displayed download count, search cards, generated files, and CI requirements synchronized as the library grows.

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

- No account or email wall
- No health-log collection in the current version
- Mobile-first, keyboard-accessible static UI
- Lightweight HTML/CSS/JavaScript
- Printable Letter-size PDF resources
- Species-specific observation fields where physiology or husbandry differs
- Clear boundary between organization and veterinary medical advice

## Support

The site support link points to `https://buymeacoffee.com/divclass016`.
