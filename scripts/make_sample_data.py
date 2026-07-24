"""Generate small synthetic national AI-strategy texts for smoke-testing.

Each generated file mixes sentences that deliberately touch several WHO
competency domains at varying intensity, so the alignment heatmap shows real
structure rather than uniform noise. Existing files are NEVER overwritten, so
this is safe to run in a directory that already holds real strategy texts.

Usage:
    python -m scripts.make_sample_data            # fill only missing countries
    python -m scripts.make_sample_data --force    # overwrite (sample data only!)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running as a script (python scripts/make_sample_data.py) or as a module.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import config  # noqa: E402

# Thematic sentence bank keyed loosely to competency domains. Countries draw
# different weighted subsets so their profiles differ.
THEMES: dict[str, list[str]] = {
    "governance": [
        "The government establishes a national AI council to coordinate policy across ministries.",
        "An institutional framework assigns clear mandates and accountability for AI oversight.",
        "Leadership and coordination bodies will steer the national digital transformation agenda.",
    ],
    "data": [
        "A data protection act safeguards personal data, privacy, and consent for citizens.",
        "Cybersecurity measures and data governance rules protect sensitive information from misuse.",
        "The strategy addresses cross-border data flows and secure storage of health records.",
    ],
    "infrastructure": [
        "Investment in broadband connectivity and data centres underpins the digital economy.",
        "Expanding mobile network coverage reduces the digital divide in rural regions.",
        "Reliable electricity and cloud infrastructure enable large-scale AI deployment.",
    ],
    "skills": [
        "Training programmes build a skilled AI workforce and data-science talent pipeline.",
        "Curricula in schools and universities strengthen digital literacy nationwide.",
        "Continuing education upskills health professionals and public servants in AI tools.",
    ],
    "innovation": [
        "Innovation hubs and research funding foster responsible artificial intelligence.",
        "The plan promotes ethical AI, machine learning research, and start-up ecosystems.",
        "Public–private partnerships accelerate emerging-technology pilots and scale-up.",
    ],
    "health": [
        "AI supports telemedicine, diagnostics, and people-centred health services.",
        "Digital health solutions improve equitable access to care in underserved communities.",
        "Clinical decision support and health data systems enhance patient outcomes.",
    ],
    "financing": [
        "A dedicated budget and investment fund sustain AI initiatives beyond pilot phases.",
        "The strategy outlines financing mechanisms and total cost of ownership.",
    ],
    "regulation": [
        "Regulatory sandboxes and certification regimes govern AI software and devices.",
        "Legislation clarifies liability and compliance for automated decision systems.",
    ],
    "monitoring": [
        "Key performance indicators and maturity assessments track implementation progress.",
        "Monitoring and evaluation frameworks generate evidence for continuous improvement.",
    ],
}

# Per-country weighting: how many times to repeat each theme (0 = absent).
# Repetition simulates emphasis, giving distinguishable heatmap rows.
COUNTRY_PROFILE: dict[str, dict[str, int]] = {
    "Kenya": {"governance": 3, "data": 2, "innovation": 3, "health": 2, "skills": 2, "infrastructure": 2, "financing": 1, "monitoring": 1},
    "Egypt": {"governance": 2, "infrastructure": 3, "skills": 3, "innovation": 2, "regulation": 2, "financing": 2},
    "Rwanda": {"governance": 3, "health": 3, "data": 2, "innovation": 2, "monitoring": 2, "skills": 1},
    "Nigeria": {"governance": 2, "innovation": 3, "skills": 2, "infrastructure": 2, "financing": 2, "data": 1},
    "South Africa": {"governance": 2, "data": 3, "regulation": 3, "innovation": 2, "monitoring": 2, "health": 1},
    "Morocco": {"infrastructure": 3, "skills": 2, "governance": 2, "innovation": 2, "financing": 1},
    "Tunisia": {"innovation": 3, "skills": 3, "governance": 1, "infrastructure": 2, "regulation": 1},
    "Ghana": {"governance": 2, "health": 2, "skills": 2, "innovation": 2, "data": 2, "infrastructure": 1},
    "Senegal": {"governance": 2, "infrastructure": 2, "innovation": 2, "financing": 1, "skills": 1},
    "Algeria": {"infrastructure": 3, "governance": 2, "skills": 2, "financing": 1},
    "Benin": {"governance": 2, "infrastructure": 2, "skills": 1, "innovation": 1},
    "Côte d'Ivoire": {"governance": 2, "infrastructure": 2, "innovation": 2, "skills": 1},
    "Namibia": {"governance": 2, "data": 1, "health": 2, "infrastructure": 2, "monitoring": 1},
    "Mauritius": {"governance": 3, "data": 2, "innovation": 3, "regulation": 2, "financing": 2, "skills": 2},
    "Zimbabwe": {"governance": 2, "infrastructure": 2, "skills": 2, "health": 1},
}

PREAMBLE = (
    "This national artificial intelligence strategy sets out the vision, guiding "
    "principles, and priority actions for {country}. It aims to harness AI for "
    "inclusive economic growth and improved public services while managing risks."
)


def build_text(country: str) -> str:
    profile = COUNTRY_PROFILE.get(country, {"governance": 2, "innovation": 2, "skills": 1})
    paragraphs = [PREAMBLE.format(country=country)]
    for theme, weight in profile.items():
        sentences = THEMES[theme]
        block = " ".join((sentences * ((weight // len(sentences)) + 1))[: max(weight, 1) * 2])
        paragraphs.append(block)
    return "\n\n".join(paragraphs) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force", action="store_true", help="overwrite existing files (sample data only)"
    )
    args = parser.parse_args()

    config.NATIONAL_DIR.mkdir(parents=True, exist_ok=True)
    written, skipped = 0, 0
    for country in config.COUNTRIES:
        path = config.country_path(country)
        if path.exists() and not args.force:
            skipped += 1
            continue
        path.write_text(build_text(country), encoding="utf-8")
        written += 1

    print(f"Sample data: wrote {written} file(s), skipped {skipped} existing.")
    print(f"Location: {config.NATIONAL_DIR}")


if __name__ == "__main__":
    main()
