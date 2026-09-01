"""Load the version-controlled Steady Paws tracker catalog."""

from __future__ import annotations

import json
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
    "small-mammal": "Small mammals",
    "bird": "Birds",
    "reptile": "Reptiles",
    "horse": "Horses",
    "aquatic": "Aquatic & amphibians",
    "universal": "Universal",
}
