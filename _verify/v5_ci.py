import pandas as pd, numpy as np
from scipy import stats
import sys
sys.path.insert(0, '.')

# --- rhetoric scores for Cote d'Ivoire exist? ---
rhet = pd.read_csv('outputs/reference_alignment/oxford_dimensions_2021_2024_embed/'
                   'oxford_dimensions_2021_2024_embed_alignment_scores.csv')
print("rhetoric countries:", sorted(rhet.country.unique()))
print("Cote in rhetoric:", [c for c in rhet.country.unique() if 'Ivoire' in c])

panel = pd.read_csv('data/oxford_readiness_indices/processed/oxford_panel_2021_2024_tidy.csv')
print("\npanel countries:", sorted(panel.country.unique()))
print("panel levels:", panel.level.unique())

dims = panel[panel.level == 'dimension']
print("\npanel dimensions:", sorted(dims.metric.unique()))
print("panel years:", sorted(dims.year.unique()))

ci = dims[(dims.country == "Cote d'Ivoire") & (dims.year.astype(str) == '2024')]
print("\n=== Cote d'Ivoire 2024 measured scores ===")
print(ci[['metric', 'score']].to_string(index=False))
