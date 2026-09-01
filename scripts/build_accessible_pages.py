"""Generate accessible HTML worksheets for every tailored Steady Paws care form."""

from __future__ import annotations

from datetime import date
from html import escape
from pathlib import Path

from build_site import ASSET_REV
from tracker_catalog import TRACKERS, condition_name

ROOT = Path(__file__).resolve().parents[1]
CARE_DIR = ROOT / "care"
SITE_URL = "https://steadypaws.netlify.app"


def care_slug(item: dict) -> str:
    return Path(item["filename"]).stem


def care_url(item: dict) -> str:
    return f"{SITE_URL}/care/{care_slug(item)}.html"


def field_id(prefix: str, value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() else "-" for ch in value.lower())
    return f"{prefix}-{cleaned.strip('-')}"


def seo_title(item: dict) -> str:
    """Keep titles descriptive and comfortably below the 70-character release gate."""
    concern = condition_name(item)
    species = item["species"]
    title = f"{concern} tracker for {species} | Steady Paws"
    if len(title) <= 70:
        return title
    compact = f"{concern} tracker | Steady Paws"
    return compact[:70].rstrip()


def seo_description(item: dict) -> str:
    """Use a consistent, useful search description that never bloats with catalog copy."""
    concern = condition_name(item).lower()
    species = item["species"].lower()
    description = (
        f"Free accessible {concern} care worksheet for {species}. "
        "Track daily changes, other conditions, and questions for their veterinary team."
    )
    if len(description) <= 180:
        return description
    short = f"Free accessible {concern} care worksheet for {species}. Track daily changes and veterinary visit notes."
    return short[:180].rstrip(" ,.;") + "."


def render_daily_table(item: dict) -> str:
    headers = "".join(f'<th scope="col">{escape(field)}</th>' for field in item["fields"])
    rows: list[str] = []
    for row_number in range(1, 12):
        cells = "".join(
            f'<td><input type="text" aria-label="{escape(field, quote=True)}, entry {row_number}" autocomplete="off"></td>'
            for field in item["fields"]
        )
        rows.append(f"<tr>{cells}</tr>")
    return (
        '<div class="table-wrap" role="region" aria-labelledby="daily-caption" tabindex="0">'
        '<table class="care-table">'
        '<caption id="daily-caption">Daily observations — 11 entries</caption>'
        f"<thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table></div>"
    )


def render_summary(item: dict) -> str:
    blocks: list[str] = []
    for index, summary in enumerate(item["summary"], start=1):
        control_id = field_id(f"summary-{index}", summary)
        blocks.append(
            '<div class="summary-item">'
            f'<label for="{control_id}">{escape(summary)}</label>'
            f'<textarea id="{control_id}" rows="3"></textarea></div>'
        )
    return "".join(blocks)


def render_page(item: dict) -> str:
    concern = condition_name(item)
    species = item["species"]
    title = seo_title(item)
    description = seo_description(item)
    canonical = care_url(item)
    pdf_url = f"/downloads/{escape(item['filename'], quote=True)}"
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <meta name="description" content="{escape(description, quote=True)}">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <meta name="theme-color" content="#55756c">
  <meta name="color-scheme" content="light">
  <link rel="canonical" href="{canonical}">
  <link rel="alternate" type="application/pdf" href="{pdf_url}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Steady Paws">
  <meta property="og:title" content="{escape(title, quote=True)}">
  <meta property="og:description" content="{escape(description, quote=True)}">
  <meta property="og:url" content="{canonical}">
  <link rel="icon" href="/assets/paw.svg?v={ASSET_REV}" type="image/svg+xml">
  <link rel="stylesheet" href="/styles/base.css?v={ASSET_REV}">
  <link rel="stylesheet" href="/styles/components.css?v={ASSET_REV}">
  <link rel="stylesheet" href="/styles/care.css?v={ASSET_REV}">
</head>
<body class="care-page">
  <a class="skip-link" href="#main">Skip to care worksheet</a>
  <header class="site-header"><div class="shell nav-wrap"><a class="brand" href="/" aria-label="Steady Paws home"><img class="brand-logo" src="/assets/paw.svg?v={ASSET_REV}" width="38" height="38" alt=""><span>Steady Paws</span></a><nav aria-label="Worksheet navigation"><a href="/#finder">Find another form</a><a href="/accessibility.html">Accessibility</a></nav></div></header>
  <main id="main" class="care-shell" itemscope itemtype="https://schema.org/WebPage">
    <header class="care-header">
      <p class="eyebrow">Accessible web worksheet · {escape(species)}</p>
      <h1 itemprop="name">{escape(concern)} care paperwork</h1>
      <p class="lede" itemprop="description">{escape(item['description'])} This web version is designed for keyboard and screen-reader use and can also be printed.</p>
      <div class="care-actions"><a class="button" href="{pdf_url}" download>Download printable PDF</a><a class="text-link" href="/#finder">Choose different paperwork <span aria-hidden="true">→</span></a></div>
      <p class="care-note" id="care-safety"><strong>Care organizer only.</strong> This worksheet does not diagnose disease or recommend treatment. Record only measurements, medicines, and care targets their veterinary team asks you to use.</p>
    </header>

    <div class="care-form" aria-describedby="care-safety">
      <fieldset class="care-fieldset">
        <legend>About your family member</legend>
        <div class="identity-grid">
          <label class="field">Their name<input type="text" autocomplete="off"></label>
          <label class="field">Week of<input type="date"></label>
          <label class="field field-wide">Their veterinarian<input type="text" autocomplete="off"></label>
          <label class="field field-wide">Primary health concern<input type="text" value="{escape(concern, quote=True)}" readonly></label>
          <label class="field field-wide">Other conditions they're living with<textarea rows="3"></textarea></label>
        </div>
      </fieldset>

      <fieldset class="care-fieldset">
        <legend>Daily observations</legend>
        {render_daily_table(item)}
      </fieldset>

      <fieldset class="care-fieldset">
        <legend>How they did this week</legend>
        <p>Use the patterns you noticed to make their next veterinary conversation easier.</p>
        <div class="summary-grid">{render_summary(item)}</div>
      </fieldset>

      <fieldset class="care-fieldset">
        <legend>Veterinary visit notes</legend>
        <label class="field">What changed since their last visit<textarea rows="5"></textarea></label>
        <label class="field">Questions for their veterinary team<textarea rows="5"></textarea></label>
        <label class="field">Their veterinary plan / next steps<textarea rows="5"></textarea></label>
      </fieldset>
    </div>

    <footer class="care-footer"><p>Steady Paws · Free family-first care paperwork · <a href="/accessibility.html">Accessibility options</a> · <a href="/privacy.html">Privacy</a></p></footer>
  </main>
</body>
</html>'''


def write_sitemap() -> None:
    urls = [f"{SITE_URL}/", f"{SITE_URL}/accessibility.html", f"{SITE_URL}/privacy.html"]
    urls.extend(care_url(item) for item in TRACKERS)
    lastmod = date.today().isoformat()
    body = "\n".join(
        f"  <url><loc>{url}</loc><lastmod>{lastmod}</lastmod></url>" for url in urls
    )
    sitemap = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}\n</urlset>\n'
    (ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    print(f"Built sitemap.xml with {len(urls)} URLs")


def main() -> int:
    CARE_DIR.mkdir(parents=True, exist_ok=True)
    for item in TRACKERS:
        path = CARE_DIR / f"{care_slug(item)}.html"
        path.write_text(render_page(item), encoding="utf-8")
    write_sitemap()
    print(f"Built {len(TRACKERS)} accessible care worksheets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
