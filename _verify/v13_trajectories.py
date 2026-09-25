import pandas as pd, numpy as np, sys
sys.path.insert(0, '.')

panel = pd.read_csv('data/oxford_readiness_indices/processed/oxford_panel_2021_2024_tidy.csv')
gov = panel[(panel.level=='pillar') & (panel.metric.str.contains('Govern', case=False, na=False))]
print("=== Government pillar, 2021-2024 (manuscript trajectory claims) ===")
piv = gov.pivot_table(index='country', columns='year', values='score')
print(piv.round(1).to_string())
print("\n=== absolute change 2021->2024 ===")
chg = (piv[2024] - piv[2021]).sort_values(ascending=False)
print(chg.round(1).to_string())
print("\n=== relative change (%) ===")
rel = ((piv[2024] - piv[2021]) / piv[2021] * 100).sort_values(ascending=False)
print(rel.round(1).to_string())
print("\n=== pillar metric names available ===")
print(panel[panel.level=='pillar'].metric.unique())
print("\n=== overall ===")
ov = panel[panel.level=='overall']
print(ov.pivot_table(index='country', columns='year', values='score').round(1).to_string())
