import pandas as pd, numpy as np, itertools
from scipy import stats

RVR = 'outputs/rhetoric_vs_readiness/rhetoric_vs_readiness.csv'
d = pd.read_csv(RVR)

def pearson(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) < 3 or a.std() == 0 or b.std() == 0: return np.nan
    return float(np.corrcoef(a, b)[0, 1])

def subsets(df):
    per = (df.groupby(['dimension', 'text_proximate'])
             .apply(lambda g: pearson(g.rhetoric_raw, g.readiness_raw), include_groups=False)
             .reset_index(name='r'))
    tp = per[per.text_proximate]['r'].mean()
    ind = per[~per.text_proximate]['r'].mean()
    return per, tp, ind

per, tp, ind = subsets(d)
print("=== BASELINE (as published, 11 countries) ===")
print(f"text-proximate mean r = {tp:+.4f}")
print(f"independent   mean r = {ind:+.4f}")
print(f"pooled r = {pearson(d.rhetoric_z, d.readiness_z):+.4f}")
print(f"n cells = {len(d)}, n countries = {d.country.nunique()}")

# --- Permutation test: enumerate all C(9,2)=36 assignments ---
print("\n=== PERMUTATION TEST (exact, dims exchangeable) ===")
dims = sorted(d.dimension.unique())
r_by_dim = per.set_index('dimension')['r'].to_dict()
obs = tp
count = 0; total = 0; vals = []
for combo in itertools.combinations(dims, 2):
    total += 1
    v = np.mean([r_by_dim[x] for x in combo])
    vals.append(v)
    if v >= obs - 1e-12: count += 1
print(f"observed text-proximate mean = {obs:+.4f}")
print(f"pairs >= observed: {count} of {total}  ->  p = {count/total:.4f}")
print(f"range of pair means: {min(vals):+.4f} to {max(vals):+.4f}")

# --- Morocco exclusion ---
print("\n=== SENSITIVITY: EXCLUDING MOROCCO ===")
d2 = d[d.country != 'Morocco']
per2, tp2, ind2 = subsets(d2)
print(f"text-proximate mean r = {tp2:+.4f}")
print(f"independent   mean r = {ind2:+.4f}")
print(f"pooled r = {pearson(d2.rhetoric_z, d2.readiness_z):+.4f}")
print(f"n countries = {d2.country.nunique()}, n cells = {len(d2)}")
obs2 = tp2; c2 = 0; t2 = 0
rb2 = per2.set_index('dimension')['r'].to_dict()
for combo in itertools.combinations(dims, 2):
    t2 += 1
    if np.mean([rb2[x] for x in combo]) >= obs2 - 1e-12: c2 += 1
print(f"permutation p (excl. Morocco) = {c2/t2:.4f} ({c2} of {t2})")
print("\nper-dim r excl Morocco:")
print(per2.to_string(index=False))
