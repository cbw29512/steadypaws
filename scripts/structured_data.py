"""Central JSON-LD builders for Your Pet’s Health Log static pages."""

from __future__ import annotations

import json
from html import escape

SITE_URL = "https://yourpetshealthlog.netlify.app"
SITE_NAME = "Your Pet’s Health Log"

# These tracker topics are useful care observations, but are not themselves
# diagnoses. They intentionally do not emit MedicalCondition schema.
NON_MEDICAL_TOPICS = {
    "Daily Quality-of-Life",
    "Feather & Skin",
    "Fish Buoyancy & Swimming",
    "Fish Skin / Gill Condition",
    "Habitat & Health",
    "Husbandry & Health",
    "Medication & Appointment Planner",
    "Senior & Mobility",
    "Senior Horse Weight & Body Condition",
    "Skin & Body-Condition",
    "Skin / Shell",
    "Water-Quality & Health",
    "Weight & Nutrition",
}


def website_node() -> dict:
    return {
        "@type": "WebSite",
        "@id": f"{SITE_URL}/#website",
        "url": f"{SITE_URL}/",
        "name": SITE_NAME,
        "description": "Free pet health trackers, printable care logs, and private phone-friendly check-ins.",
    }


def json_ld_script(graph: list[dict]) -> str:
    payload = {
        "@context": "https://schema.org",
        "@graph": graph,
    }
    # Escape closing tags defensively while keeping readable JSON-LD.
    serialized = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return f'<script type="application/ld+json">{serialized}</script>'


def homepage_json_ld(*, title: str, description: str, faq_items: list[tuple[str, str]]) -> str:
    page_id = f"{SITE_URL}/#collection"
    graph: list[dict] = [
        website_node(),
        {
            "@type": "CollectionPage",
            "@id": page_id,
            "url": f"{SITE_URL}/",
            "name": title,
            "description": description,
            "isPartOf": {"@id": f"{SITE_URL}/#website"},
            "about": {
                "@type": "Thing",
                "name": "Pet health tracking and veterinary visit preparation",
            },
        },
    ]
    if faq_items:
        graph.append(
            {
                "@type": "FAQPage",
                "@id": f"{SITE_URL}/#faq",
                "url": f"{SITE_URL}/#tracker-faq-title",
                "isPartOf": {"@id": page_id},
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": question,
                        "acceptedAnswer": {"@type": "Answer", "text": answer},
                    }
                    for question, answer in faq_items
                ],
            }
        )
    return json_ld_script(graph)


def care_page_json_ld(
    *,
    canonical: str,
    title: str,
    description: str,
    concern: str,
    species: str,
    is_medical_condition: bool,
) -> str:
    page_id = f"{canonical}#webpage"
    graph: list[dict] = [
        website_node(),
        {
            "@type": "WebPage",
            "@id": page_id,
            "url": canonical,
            "name": title,
            "description": description,
            "isPartOf": {"@id": f"{SITE_URL}/#website"},
            "about": {
                "@type": "Thing",
                "name": f"{species} {concern}".strip(),
            },
        },
    ]
    if is_medical_condition:
        condition_id = f"{canonical}#condition"
        graph[1]["mainEntity"] = {"@id": condition_id}
        graph.append(
            {
                "@type": "MedicalCondition",
                "@id": condition_id,
                "name": concern,
                "description": f"Pet health tracking worksheet for {species.lower()} care related to {concern.lower()}.",
            }
        )
    return json_ld_script(graph)


def is_medical_topic(concern: str, group: str) -> bool:
    return group != "universal" and concern not in NON_MEDICAL_TOPICS
