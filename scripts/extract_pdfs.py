"""Extract text from source strategy PDFs into the .txt files the pipeline reads.

National-strategy PDFs in ``data/national_strategies/`` are matched to their
canonical ``<country>_ai.txt`` target (from ``config.COUNTRY_FILES``) by fuzzy
country-name matching on the filename. The WHO strategy PDF, if present, is
written to ``config.WHO_STRATEGY_TXT``.

Existing .txt targets are skipped unless ``--force`` is given.

    python -m scripts.extract_pdfs           # extract what is missing
    python -m scripts.extract_pdfs --force   # re-extract everything
    python -m scripts.extract_pdfs --list    # show the PDF -> target mapping only
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pdfplumber  # noqa: E402

from src import config, preprocess  # noqa: E402


# Explicit overrides for PDFs whose filename does not contain the country name.
# Key: an accent-folded, alphanumeric substring uniquely identifying the file
# (see _norm_name — digits are kept, so dated filenames can be disambiguated).
FILENAME_OVERRIDES: dict[str, str] = {
    "strategienationale": "Côte d'Ivoire",  # French title, no country in name
    "bigdata": "Benin",                      # "National AI and Big Data Strategy" (SNIAM)
    "19092025": "Nigeria",                   # generic "National AI Strategy", dated 19/09/2025
}


def _norm_name(text: str) -> str:
    """Lowercase, strip accents, keep letters AND digits (for override matching)."""
    decomposed = unicodedata.normalize("NFKD", text)
    ascii_only = "".join(c for c in decomposed if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", ascii_only.lower())


def _slug(text: str) -> str:
    """Like _norm_name but letters only — so 'Côte d'Ivoire' -> 'cotedivoire'."""
    return re.sub(r"[0-9]", "", _norm_name(text))


def match_country(pdf_name: str) -> str | None:
    """Best-effort match of a PDF filename to a configured country."""
    norm = _norm_name(pdf_name)
    for needle, country in FILENAME_OVERRIDES.items():
        if needle in norm:
            return country

    slug = _slug(pdf_name)

    best: tuple[int, str] | None = None
    for country in config.COUNTRIES:
        key = _slug(country)
        if key and key in slug:
            # Prefer the longest country name matched (handles "South Africa").
            if best is None or len(key) > best[0]:
                best = (len(key), country)
    return best[1] if best else None


def extract_text(pdf_paths: list[Path]) -> str:
    """Extract and concatenate text from one or more PDFs.

    When a country maps to several PDFs (e.g. an AI strategy plus a digital-health
    roadmap), they are concatenated into a single document, separated by a short
    provenance marker. The marker is far below the chunker's minimum length, so it
    is dropped and never pollutes the embeddings.
    """
    parts: list[str] = []
    for pdf_path in pdf_paths:
        with pdfplumber.open(pdf_path) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
        body = preprocess.clean_text("\n\n".join(pages))
        if len(pdf_paths) > 1:
            parts.append(f"\n\n== source: {pdf_path.name} ==\n\n{body}")
        else:
            parts.append(body)
    return "\n".join(parts).strip()


def plan() -> tuple[dict[str, tuple[Path, list[Path]]], list[Path]]:
    """Group national PDFs by matched country and pick the WHO reference.

    Returns:
        countries: {country -> (txt_target, [pdf_paths])}, sorted by filename
        unmatched: PDFs whose country could not be determined
    """
    countries: dict[str, tuple[Path, list[Path]]] = {}
    unmatched: list[Path] = []

    for pdf in sorted(config.NATIONAL_DIR.glob("*.pdf")):
        country = match_country(pdf.name)
        if country is None:
            unmatched.append(pdf)
            continue
        target = config.country_path(country)
        countries.setdefault(country, (target, []))[1].append(pdf)

    who_pdfs = sorted(config.WHO_DIR.glob("*.pdf"))
    # Prefer the most recent strategy (the 2020-2027 extension) as the reference.
    who_pdfs.sort(key=lambda p: ("2027" not in p.name, p.name))
    if who_pdfs:
        countries["WHO reference"] = (config.WHO_STRATEGY_TXT, [who_pdfs[0]])

    return countries, unmatched


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--force", action="store_true", help="overwrite existing .txt targets")
    ap.add_argument("--list", action="store_true", help="print the mapping and exit")
    args = ap.parse_args()

    countries, unmatched = plan()
    if not countries and not unmatched:
        print(f"No PDFs found under {config.DATA_DIR}.")
        return 1

    print("PDF -> target mapping:")
    for country, (target, pdfs) in countries.items():
        multi = f"  (x{len(pdfs)} concatenated)" if len(pdfs) > 1 else ""
        print(f"  [{country:14s}] -> {target.name}{multi}")
        for pdf in pdfs:
            print(f"        + {pdf.name}")
    for pdf in unmatched:
        print(f"  [??? unmatched ] {pdf.name}")
    if args.list:
        return 0

    print()
    written = skipped = failed = len(unmatched)
    for pdf in unmatched:
        print(f"  ! skipped (no country match): {pdf.name}")

    for country, (target, pdfs) in countries.items():
        if target.exists() and not args.force:
            skipped += 1
            continue
        try:
            text = extract_text(pdfs)
        except Exception as exc:  # noqa: BLE001 — report and continue
            print(f"  ! failed to extract {country}: {exc}")
            failed += 1
            continue
        target.write_text(text, encoding="utf-8")
        note = f" (from {len(pdfs)} PDFs)" if len(pdfs) > 1 else ""
        print(f"  wrote {target.name}  ({len(text.split()):,} words){note}")
        written += 1

    print(f"\nDone: {written} written, {skipped} skipped, {failed} unmapped/failed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
