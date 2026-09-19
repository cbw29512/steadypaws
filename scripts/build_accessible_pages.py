"""Generate accessible HTML worksheets for every tailored Your Pet’s Health Log care form."""

from __future__ import annotations

from datetime import date
from html import escape
import json
from pathlib import Path

from build_site import ASSET_REV
from build_trackers import display_field
from tracker_catalog import TRACKERS, condition_name

ROOT = Path(__file__).resolve().parents[1]
CARE_DIR = ROOT / "care"
SITE_URL = "https://yourpetshealthlog.netlify.app"
CARE_ASSET_REV = "20260919-trust-content2"

SPECIES_CONTEXT = {
    "Cat": "For cats, consistent notes can make quiet day-to-day changes easier to describe later. This version keeps the selected concern tied to repeatable home observations without asking you to interpret the cause.",
    "Dog": "For dogs, routines such as meals, walks, activity, sleep, and bathroom habits can create a useful timeline. This version keeps the selected concern organized around repeatable observations you can bring to a visit.",
    "Rabbit": "Rabbits often benefit from careful routine notes because eating, droppings, posture, movement, and behavior can change together. This version keeps those observations organized without turning them into a diagnosis.",
    "Guinea Pig": "For guinea pigs, small changes in eating, weight, movement, breathing, or daily routine can be hard to reconstruct from memory. This version gives those observations a consistent place to live.",
    "Ferret": "For ferrets, appetite, energy, weight, movement, breathing, and episode notes can be easier to compare when they are recorded the same way each time. This version is built around that consistency.",
    "Chinchilla": "For chinchillas, eating, droppings, weight, movement, coat or skin changes, and environmental notes can be useful to keep together. This version emphasizes repeatable observations rather than interpretation.",
    "Hamster": "For hamsters, brief daily notes can preserve small changes in appetite, weight, activity, grooming, breathing, or a visible lump that might otherwise be difficult to remember later.",
    "Rat / Mouse": "For rats and mice, weight, appetite, breathing, mobility, grooming, and social behavior can change quickly enough that a simple written timeline is useful. This version keeps that history together.",
    "Bird": "For birds, weight, appetite, droppings, breathing, perching, activity, feathers, and voice can all be useful parts of a home observation record. This version keeps those notes consistent and easy to review.",
    "Reptile": "For reptiles, health observations often make more sense beside husbandry notes such as temperature, humidity, UVB, feeding, shedding, and activity. This version keeps the relevant environment and body observations together.",
    "Horse": "For horses, repeated notes about movement, work tolerance, body condition, appetite, hooves, breathing, and medication can make trends easier to discuss with the veterinary and farrier teams.",
    "Aquarium Fish": "For aquarium fish, body and behavior observations are most useful when water conditions and maintenance are recorded alongside them. This version keeps those details on the same timeline.",
    "Amphibian": "For amphibians, skin, posture, appetite, activity, weight, temperature, humidity, or water conditions can be useful to record together. This version keeps the environment and visible changes connected.",
    "All Pets": "This general-purpose tracker is designed for observations that apply across many species and keeps the record focused on what happened, when it happened, and what you want to discuss next.",
}


def care_slug(item: dict) -> str:
    return Path(item["filename"]).stem


def care_url(item: dict) -> str:
    return f"{SITE_URL}/care/{care_slug(item)}.html"


def field_id(prefix: str, value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() else "-" for ch in value.lower())
    return f"{prefix}-{cleaned.strip('-')}"


def tracker_heading(item: dict) -> str:
    concern = condition_name(item)
    species = item["species"].strip()
    if item["group"] == "universal" or species.lower() in {"all pets", "all"}:
        return f"{concern} Pet Health Tracker"
    return f"{species} {concern} Tracker"


def seo_title(item: dict) -> str:
    title = f"Free {tracker_heading(item)} | Your Pet’s Health Log"
    if len(title) <= 70:
        return title
    compact = f"{tracker_heading(item)} | Your Pet’s Health Log"
    return compact[:70].rstrip()


def seo_description(item: dict) -> str:
    heading = tracker_heading(item).lower()
    details = item["description"].strip().rstrip(".")
    description = f"Free {heading}. Track {details.lower()}. Print the PDF or use the accessible web worksheet for vet-visit notes."
    if len(description) <= 180:
        return description
    short = f"Free {heading}. Track daily changes and keep organized notes for veterinary visits. Printable PDF and accessible web worksheet."
    return short[:180].rstrip(" ,.;") + "."


def medical_condition_node(item: dict, canonical: str) -> dict | None:
    concern = condition_name(item)
    non_conditions = (
        "health log", "weight & nutrition", "senior", "quality-of-life",
        "medication & appointment", "husbandry",
    )
    if item["group"] == "universal" or any(term in concern.lower() for term in non_conditions):
        return None
    return {
        "@type": "MedicalCondition",
        "@id": f"{canonical}#condition",
        "name": concern,
    }


def page_json_ld(item: dict, heading: str, description: str, canonical: str) -> str:
    graph: list[dict] = [
        {
            "@type": "WebSite",
            "@id": f"{SITE_URL}/#website",
            "url": f"{SITE_URL}/",
            "name": "Your Pet’s Health Log",
        },
        {
            "@type": "WebPage",
            "@id": f"{canonical}#webpage",
            "url": canonical,
            "name": heading,
            "description": description,
            "isPartOf": {"@id": f"{SITE_URL}/#website"},
        },
    ]
    condition = medical_condition_node(item, canonical)
    if condition:
        graph.append(condition)
        graph[1]["about"] = {"@id": condition["@id"]}
    payload = {"@context": "https://schema.org", "@graph": graph}
    return '<script type="application/ld+json">' + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "</script>"


def natural_list(values: list[str]) -> str:
    cleaned = [display_field(value) for value in values]
    if not cleaned:
        return ""
    if len(cleaned) == 1:
        return cleaned[0]
    if len(cleaned) == 2:
        return f"{cleaned[0]} and {cleaned[1]}"
    return ", ".join(cleaned[:-1]) + f", and {cleaned[-1]}"


def render_tracker_context(item: dict) -> str:
    species = item["species"].strip()
    concern = condition_name(item)
    context = SPECIES_CONTEXT.get(species, SPECIES_CONTEXT["All Pets"])
    daily = natural_list(item["fields"])
    review = natural_list(item["summary"][:4])
    if species == "Cat":
        more_link = '<p><a class="text-link" href="/pets/cat-health-trackers.html">Browse more cat health trackers <span aria-hidden="true">→</span></a></p>'
    elif species == "Dog":
        more_link = '<p><a class="text-link" href="/pets/dog-health-trackers.html">Browse more dog health trackers <span aria-hidden="true">→</span></a></p>'
    else:
        more_link = '<p><a class="text-link" href="/#finder">Browse trackers for another pet or concern <span aria-hidden="true">→</span></a></p>'
    return (
        '<section class="care-context" aria-labelledby="tracker-focus">'
        f'<h2 id="tracker-focus">What this {escape(species.lower())} {escape(concern.lower())} tracker records</h2>'
        f'<p>{escape(context)}</p>'
        f'<p><strong>Daily record:</strong> {escape(daily)}. '
        f'<strong>Review before the next visit:</strong> {escape(review)}.</p>'
        '<p>These are observation prompts, not medical targets or instructions. Use the fields that match the plan from your veterinary team and leave the rest blank when they do not apply.</p>'
        f'{more_link}</section>'
    )


def render_daily_table(item: dict) -> str:
    headers = "".join(f'<th scope="col">{escape(display_field(field))}</th>' for field in item["fields"])
    rows: list[str] = []
    for row_number in range(1, 12):
        cells = "".join(
            f'<td><input type="text" aria-label="{escape(display_field(field), quote=True)}, entry {row_number}" autocomplete="off"></td>'
            for field in item["fields"]
        )
        rows.append(f"<tr>{cells}</tr>")
    return (
        '<div class="table-wrap" role="region" aria-labelledby="daily-caption" tabindex="0">'
        '<table class="care-table">'
        '<caption id="daily-caption">Daily care log — use one row each time you check or give care.</caption>'
        f"<thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table></div>"
    )


def render_summary(item: dict) -> str:
    blocks: list[str] = []
    for index, summary in enumerate(item["summary"], start=1):
        label = display_field(summary)
        control_id = field_id(f"summary-{index}", label)
        blocks.append(
            '<div class="summary-item">'
            f'<label for="{control_id}">{escape(label)}</label>'
            f'<textarea id="{control_id}" rows="3"></textarea></div>'
        )
    return "".join(blocks)


def render_page(item: dict) -> str:
    concern = condition_name(item)
    species = item["species"]
    heading = tracker_heading(item)
    title = seo_title(item)
    description = seo_description(item)
    canonical = care_url(item)
    pdf_url = f"/downloads/{escape(item['filename'], quote=True)}"
    intro = item["description"].strip().rstrip(".")
    json_ld = page_json_ld(item, heading, description, canonical)
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
  <meta property="og:site_name" content="Your Pet’s Health Log">
  <meta property="og:title" content="{escape(title, quote=True)}">
  <meta property="og:description" content="{escape(description, quote=True)}">
  <meta property="og:url" content="{canonical}">
  <link rel="icon" href="/assets/paw.svg?v={ASSET_REV}" type="image/svg+xml">
  <link rel="stylesheet" href="/styles/base.css?v={ASSET_REV}">
  <link rel="stylesheet" href="/styles/components.css?v={ASSET_REV}">
  <link rel="stylesheet" href="/styles/care.css?v={CARE_ASSET_REV}">
  <script src="/assets/care-personalization-print1.js?v={CARE_ASSET_REV}" defer></script>
  <script src="/assets/care-autosave.js?v={ASSET_REV}" defer></script>
  <script src="/assets/offline.js?v={ASSET_REV}" defer></script>
  {json_ld}
</head>
<body class="care-page">
  <a class="skip-link" href="#main">Skip to pet health tracker</a>
  <header class="site-header"><div class="shell nav-wrap"><a class="brand" href="/" aria-label="Your Pet’s Health Log home"><img class="brand-logo" src="/assets/paw.svg?v={ASSET_REV}" width="38" height="38" alt=""><span>Your Pet’s Health Log</span></a><nav aria-label="Tracker navigation"><a href="/#finder">Find another pet health tracker</a><a href="/accessibility.html">Accessibility</a></nav></div></header>
  <main id="main" class="care-shell">
    <header class="care-header">
      <p class="eyebrow">Free pet health tracker · {escape(species)}</p>
      <h1>{escape(heading)}</h1>
      <p class="lede">Use this simple tracker to record {escape(intro.lower())}. Keep the important details together for the days between veterinary visits.</p>
      <div class="care-actions">
        <a class="button" href="{pdf_url}" download>Download printable PDF</a>
        <button id="care-print-personalized" class="button care-print-button" type="button">Print this worksheet</button>
        <button id="clear-care-form-data" class="button button-secondary" type="button">Clear Form Data</button>
        <a class="text-link" href="/#finder">Choose a different pet health tracker <span aria-hidden="true">→</span></a>
      </div>
      <p id="care-personalization-status" class="care-personalization-status" role="status">Tip: add a name or photo on the Your Pet’s Health Log finder page before opening this tracker if you want it included when printing.</p>
      <p id="care-autosave-status" class="care-personalization-status" role="status">Worksheet entries auto-save only in this browser on this device.</p>
      <p class="care-note" id="care-safety"><strong>For organizing care, not medical advice.</strong> Follow their veterinarian's plan and contact a veterinarian for urgent or concerning changes.</p>
    </header>

    {render_tracker_context(item)}

    <div class="care-form" aria-describedby="care-safety">
      <fieldset class="care-fieldset">
        <legend>Care details</legend>
        <div class="identity-grid">
          <label class="field">Their name<input id="care-family-name" type="text" autocomplete="off"></label>
          <label class="field">Week of<input type="date"></label>
          <label class="field field-wide">Veterinarian<input type="text" autocomplete="off"></label>
          <label class="field field-wide">Main health concern<input type="text" value="{escape(concern, quote=True)}" readonly></label>
          <label class="field field-wide">Other health conditions<textarea rows="3"></textarea></label>
        </div>
      </fieldset>

      <fieldset class="care-fieldset">
        <legend>Daily care log</legend>
        {render_daily_table(item)}
      </fieldset>

      <fieldset class="care-fieldset">
        <legend>This week at a glance</legend>
        <p>Note the changes or patterns that matter most.</p>
        <div class="summary-grid">{render_summary(item)}</div>
      </fieldset>

      <fieldset class="care-fieldset">
        <legend>Vet visit notes</legend>
        <label class="field">Since the last vet visit<textarea rows="5"></textarea></label>
        <label class="field">Questions for the vet<textarea rows="5"></textarea></label>
        <label class="field">Plan / next steps from the vet<textarea rows="5"></textarea></label>
      </fieldset>
    </div>

    <footer class="care-footer"><p>Your Pet’s Health Log · Free pet health trackers for animals you love · <a href="/accessibility.html">Accessibility options</a> · <a href="/privacy.html">Privacy</a></p></footer>
  </main>
</body>
</html>'''


def write_sitemap() -> None:
    urls = [f"{SITE_URL}/", f"{SITE_URL}/about.html", f"{SITE_URL}/accessibility.html", f"{SITE_URL}/privacy.html"]
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
    print(f"Built {len(TRACKERS)} accessible pet health tracker worksheets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
