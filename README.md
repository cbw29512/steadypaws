# Steady Paws

Steady Paws is a free, privacy-conscious chronic-care tracker library for dog and cat owners. The site provides printable organizational tools designed to make day-to-day observations easier to record and discuss with a veterinary team.

Live site: https://steadypaws.netlify.app/

## Current library

The production library contains **22 two-page printable PDFs**:

- 10 cat trackers
- 10 dog trackers
- 2 universal chronic-care tools

Every tracker includes a daily log plus a weekly summary / veterinary appointment-prep page. The site does not diagnose, prescribe, recommend medication doses, or replace veterinary care.

## Production design

- Responsive, keyboard-accessible interface
- Searchable tracker library with Cat / Dog / Universal filters
- No account or email wall
- No analytics or pet-health log collection in the current version
- Direct PDF downloads
- Canonical URL, sitemap, crawler configuration and social metadata
- Netlify security and cache headers
- Buy Me a Coffee support link

## Reproducible PDF generation

Tracker PDFs are generated from version-controlled specifications in `scripts/build_trackers.py` using ReportLab. This keeps the entire library consistent and makes global fixes reproducible instead of maintaining dozens of unrelated binary files by hand.

Generate locally:

```bash
python -m pip install -r requirements.txt
python scripts/build_trackers.py
python scripts/verify_site.py
```

## Quality gate

GitHub Actions regenerates the complete library on every push and pull request, then verifies:

- all required production files
- all 22 homepage download links
- valid two-page PDF output
- internal links
- canonical production URL
- robots / sitemap configuration
- required support link

## Netlify deployment

`netlify.toml` installs the pinned PDF dependency and runs the tracker generator during each deployment. The repository root is published after generation, so every production deploy contains the complete current tracker library.

## Important boundary

Steady Paws provides organizational tools, not diagnosis or treatment. Pet owners should follow their veterinary team's instructions and seek veterinary or emergency veterinary care for urgent or concerning changes.

## Support

Support Steady Paws at https://buymeacoffee.com/divclass016.
