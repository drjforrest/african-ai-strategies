"""AI-strategy × WHO digital-health competency alignment pipeline.

Quantitatively maps 15 African national AI strategies onto WHO Global Strategy
on Digital Health competency domains via sentence-transformer embeddings.
"""

from __future__ import annotations

__version__ = "0.1.0"

# Submodules (config, preprocess, models, competencies, alignment, visualize)
# are imported explicitly by callers, e.g. ``from src import alignment``. They
# are intentionally not eagerly imported here so that lightweight modules
# (config, preprocess) can be used without pulling in matplotlib/seaborn.
