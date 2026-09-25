import pandas as pd, numpy as np
from scipy import stats
d = pd.read_csv('outputs/rhetoric_vs_readiness/rhetoric_vs_readiness.csv')
print("countries:", len(d.country.unique()))
print(sorted(d.country.unique()))
print("cells:", len(d), "dims:", d.dimension.nunique())

r = d.groupby(['dimension','text_proximate'], group_keys=False).apply(
    lambda g: pd.Series({'r': stats.pearsonr(g.rhetoric_z, g.readiness_z)[0], 'n': len(g)}),
    include_groups=False)
print(r)
tp = r[r.index.get_level_values(1)]['r']
ind = r[~r.index.get_level_values(1)]['r']
print("text-proximate mean r:", round(tp.mean(),4))
print("independent mean r:", round(ind.mean(),4))
print("pooled r:", round(stats.pearsonr(d.rhetoric_z, d.readiness_z)[0],4))
