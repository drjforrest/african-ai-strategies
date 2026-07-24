"""Text loading, cleaning, and chunking.

Kept intentionally dependency-light (stdlib only) so it is trivially testable
and importable without the heavy ML stack. PDF extraction is *not* done here:
convert PDFs to ``.txt`` up front (see README) and feed the text in.
"""

from __future__ import annotations

import re
from pathlib import Path

from . import config


def load_text(path: str | Path) -> str:
    """Read a UTF-8 text file, tolerating stray encoding errors."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Strategy text not found: {path}")
    return path.read_text(encoding="utf-8", errors="replace")


# Matches page-number / running-header lines like "Page 12", "12 | WHO", bare
# numbers on their own line, and form-feed characters left by PDF extraction.
_HEADER_FOOTER_RE = re.compile(
    r"^\s*(page\s+\d+|\d+\s*\|.*|\d+)\s*$",
    flags=re.IGNORECASE | re.MULTILINE,
)
_HYPHEN_LINEBREAK_RE = re.compile(r"(\w)-\n(\w)")   # "inter-\noperability" -> join
_MULTISPACE_RE = re.compile(r"[ \t]+")
_MULTINEWLINE_RE = re.compile(r"\n{3,}")

# PDF extraction frequently misreads the "AI" ligature as "Al" (capital-I
# rendered as lowercase-L), corrupting the single most important token in this
# corpus — e.g. "Al governance", "Al/ML", "Al-related". Repair standalone "Al"
# -> "AI", but preserve genuine Arabic proper names carrying the "al-" article
# (e.g. "Al Jazari", "Al-Azhar"): a hyphen + capital ("Al-Azhar") or a known
# name word after a space is left untouched.
_AI_MISREAD_RE = re.compile(
    r"\bAl\b"
    r"(?!-[A-Z])"
    r"(?!\s+(?:Jazari|Jazeera|Azhar|Khwarizmi)\b)"
)


def clean_text(text: str, *, lowercase: bool = False) -> str:
    """Normalise whitespace and strip common PDF extraction artefacts.

    Lowercasing is optional and defaults off: sentence-transformer models are
    cased and generally do better with original casing. The TF-IDF fallback
    lowercases internally regardless, so behaviour stays consistent.
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\f", "\n")
    text = _HYPHEN_LINEBREAK_RE.sub(r"\1\2", text)
    text = _AI_MISREAD_RE.sub("AI", text)
    text = _HEADER_FOOTER_RE.sub("", text)
    text = _MULTISPACE_RE.sub(" ", text)
    text = _MULTINEWLINE_RE.sub("\n\n", text)
    text = text.strip()
    if lowercase:
        text = text.lower()
    return text


def _split_paragraphs(text: str) -> list[str]:
    """Split on blank lines, falling back to single newlines if the document
    has no paragraph breaks at all."""
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    if len(paras) <= 1:
        paras = [p.strip() for p in text.split("\n") if p.strip()]
    return paras


def chunk_text(
    text: str,
    max_tokens: int = config.CHUNK_SIZE_TOKENS,
    *,
    overlap: int = config.CHUNK_OVERLAP_TOKENS,
    min_tokens: int = config.MIN_CHUNK_TOKENS,
) -> list[str]:
    """Chunk into ~``max_tokens``-word passages.

    Strategy: pack whole paragraphs together until adding the next one would
    exceed ``max_tokens``. Paragraphs longer than ``max_tokens`` on their own
    are hard-split with a sliding window (``overlap`` words of context carried
    forward). Chunks shorter than ``min_tokens`` are dropped as noise.

    "Tokens" here means whitespace-delimited words — a fast, model-agnostic
    proxy. The embedding model applies its own subword tokenizer downstream.
    """
    if max_tokens <= 0:
        raise ValueError("max_tokens must be positive")
    overlap = max(0, min(overlap, max_tokens - 1))

    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    def flush() -> None:
        nonlocal current, current_len
        if current:
            chunks.append(" ".join(current))
            current, current_len = [], 0

    for para in _split_paragraphs(text):
        words = para.split()
        if not words:
            continue

        if len(words) > max_tokens:
            flush()
            step = max_tokens - overlap
            for start in range(0, len(words), step):
                window = words[start : start + max_tokens]
                if window:
                    chunks.append(" ".join(window))
                if start + max_tokens >= len(words):
                    break
            continue

        if current_len + len(words) > max_tokens:
            flush()
        current.extend(words)
        current_len += len(words)

    flush()
    return [c for c in chunks if len(c.split()) >= min_tokens]


def load_and_chunk(path: str | Path, **chunk_kwargs) -> list[str]:
    """Convenience: load -> clean -> chunk in one call."""
    return chunk_text(clean_text(load_text(path)), **chunk_kwargs)
