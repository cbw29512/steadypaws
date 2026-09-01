"""Load and normalize the version-controlled Steady Paws care-form catalog."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_DIR = ROOT / "data" / "trackers"
CATALOG_FILES = (
    "cat.json", "dog.json", "rabbit.json", "guinea-pig.json", "ferret.json", "chinchilla.json",
    "hamster.json", "rat-mouse.json", "bird.json", "reptile.json", "horse.json", "aquatic.json", "universal.json",
)

TRACKERS: list[dict] = []
for filename in CATALOG_FILES:
    TRACKERS.extend(json.loads((CATALOG_DIR / filename).read_text(encoding="utf-8")))

GROUP_LABELS = {
    "all": "All",
    "cat": "Cats",
    "dog": "Dogs",
    "small-mammal": "Small & furry",
    "bird": "Birds",
    "reptile": "Reptiles",
    "horse": "Horses",
    "aquatic": "Fish & amphibians",
    "universal": "Any pet",
}


def base_condition_title(item: dict) -> str:
    """Remove species wording that belongs to the form variant, not the condition."""
    title = item["title"].strip()
    prefixes = (
        f'{item["species"]} ',
        "Feline ",
        "Canine ",
        "Equine ",
        "Avian ",
        "Pet Bird ",
    )
    for prefix in prefixes:
        if title.lower().startswith(prefix.lower()):
            title = title[len(prefix):]
            break
    for suffix in (" Tracker", " Log"):
        if title.endswith(suffix):
            title = title[:-len(suffix)]
            break
    return title.strip()


def condition_name(item: dict) -> str:
    """Return the shared, human-facing primary health concern for a form variant."""
    title = base_condition_title(item)
    lowered = title.lower()

    if "diabetes" in lowered:
        return "Diabetes"
    if "chronic kidney disease" in lowered or lowered == "kidney disease":
        return "Kidney Disease"
    if "arthritis" in lowered:
        return "Arthritis & Mobility"
    if "heart disease" in lowered:
        return "Heart Disease"
    if "seizure" in lowered or "epilepsy" in lowered:
        return "Seizures / Epilepsy"
    if "cancer" in lowered or "tumor" in lowered:
        return "Cancer / Tumor & Supportive Care"
    if "dental" in lowered:
        return "Dental Problems"
    if "respiratory" in lowered and "asthma" not in lowered:
        return "Respiratory Problems"
    if any(term in lowered for term in ("chronic gi", "gi / appetite", "appetite & digestive")):
        return "Digestive / GI Problems"
    if "metabolic bone disease" in lowered:
        return "Metabolic Bone Disease"
    return title


def condition_key(item: dict) -> str:
    """Stable DOM/search key for a shared health concern."""
    key = re.sub(r"[^a-z0-9]+", "-", condition_name(item).lower()).strip("-")
    if not key:
        raise ValueError(f"Could not derive condition key for {item['filename']}")
    return key


CONDITION_NAMES = sorted({condition_name(item) for item in TRACKERS}, key=str.casefold)
