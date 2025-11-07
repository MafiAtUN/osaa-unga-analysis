"""Utility helpers for working with region and country groupings."""

from __future__ import annotations

import re
from typing import Dict, Iterable, List, Set, Tuple

from src.unga_analysis.data.data_ingestion import (
    COUNTRY_CODE_MAPPING,
    get_all_region_labels,
    get_country_region_lookup,
)


_COUNTRY_ALIASES: Dict[str, str] = {
    "us": "United States",
    "usa": "United States",
    "united states of america": "United States",
    "america": "United States",
    "uk": "United Kingdom",
    "britain": "United Kingdom",
    "great britain": "United Kingdom",
    "u k": "United Kingdom",
    "drc": "Democratic Republic of the Congo",
    "congo democratic republic": "Democratic Republic of the Congo",
    "republic of congo": "Republic of the Congo",
    "s korea": "South Korea",
    "n korea": "North Korea",
}


def _normalize(text: str) -> str:
    """Lowercase and strip punctuation for comparison."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def expand_regions_to_countries(regions: Iterable[str]) -> List[str]:
    """Return a sorted list of countries that belong to any of the provided regions."""
    region_set = {region for region in regions if region}
    if not region_set:
        return []

    country_region_lookup = get_country_region_lookup()
    selected: Set[str] = set()

    for country, labels in country_region_lookup.items():
        if any(region in labels for region in region_set):
            selected.add(country)

    return sorted(selected)


def extract_regions_and_countries(text: str) -> Tuple[List[str], List[str]]:
    """Detect region labels and explicit country references within free-form text."""

    if not text:
        return [], []

    normalized_text = _normalize(text)
    regions: Set[str] = set()
    countries: Set[str] = set()

    # Build lookup caches
    country_region_lookup = get_country_region_lookup()
    region_labels = [label for label in get_all_region_labels() if label and label.lower() != "unknown"]

    country_lookup: Dict[str, str] = {}
    for _code, name in COUNTRY_CODE_MAPPING.items():
        norm_name = _normalize(name)
        if norm_name:
            country_lookup[norm_name] = name

    country_lookup.update(_COUNTRY_ALIASES)

    # Detect explicit country mentions
    for alias, canonical in country_lookup.items():
        if alias and alias in normalized_text:
            countries.add(canonical)

    # Region label detection
    region_aliases: Dict[str, str] = {}
    replacements = {
        "northern": "north",
        "southern": "south",
        "western": "west",
        "eastern": "east",
        "central": "central",
    }

    for label in region_labels:
        norm_label = _normalize(label)
        if not norm_label:
            continue

        variants = {norm_label, norm_label.replace("-", " ")}
        for old, new in replacements.items():
            if old in norm_label:
                variants.add(norm_label.replace(old, new))

        for variant in variants:
            region_aliases[variant] = label

    for alias, label in region_aliases.items():
        if alias and alias in normalized_text:
            regions.add(label)

    # Generic macro terms for backward compatibility
    generic_terms = {
        "africa": "Africa",
        "asia": "Asia",
        "europe": "Europe",
        "north america": "North America",
        "south america": "South America",
        "latin america": "Latin America and the Caribbean",
        "caribbean": "Caribbean",
        "oceania": "Oceania",
        "middle east": "Western Asia",
        "americas": "Americas",
        "pacific": "Pacific",
        "small island states": "Small Island Developing States (SIDS)",
        "sids": "Small Island Developing States (SIDS)",
    }

    for term, label in generic_terms.items():
        if term in normalized_text:
            regions.add(label)

    # Drop generic parents when a more specific label is detected
    parents = {
        "Africa",
        "Asia",
        "Europe",
        "North America",
        "South America",
        "Oceania",
        "Latin America and the Caribbean",
    }
    to_remove: Set[str] = set()
    for parent in parents & regions:
        for label in regions:
            if label != parent and parent.lower() in _normalize(label):
                to_remove.add(parent)
                break
    regions -= to_remove

    # Expand detected regions to countries (and add to countries set)
    if regions:
        countries.update(expand_regions_to_countries(regions))

    return sorted(regions), sorted(countries)

