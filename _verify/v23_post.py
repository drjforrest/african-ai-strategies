import pandas as pd, numpy as np
print("=== Table S1 / convergence unchanged? ===")
c = pd.read_csv('outputs/au_convergence/au_convergence.csv')
print(c[['country','profile_r_to_AU','rank']].round(3).to_string(index=False))

print("\n=== Figure 1 source (alignment_scores.csv) unchanged? ===")
al = pd.read_csv('outputs/alignment_scores.csv')
print("rows:", len(al), "countries:", al.country.nunique())
print("min/max/mean:", round(al.similarity_score.min(),4), round(al.similarity_score.max(),4),
      round(al.similarity_score.mean(),4))

print("\n=== Figure 2 source (corrected, 12 countries) ===")
d = pd.read_csv('outputs/rhetoric_vs_readiness/rhetoric_vs_readiness.csv')
print("cells:", len(d), "countries:", d.country.nunique())
print(d.groupby('country').size().to_string())

print("\n=== per-dimension r (Figure 2 right panel) ===")
p = pd.read_csv('outputs/rhetoric_vs_readiness/per_dimension_correlation.csv')
print(p.round(4).to_string(index=False))

print("\n=== quadrants, corrected 12-country ===")
print(pd.crosstab(d.country, d.quadrant).to_string())
