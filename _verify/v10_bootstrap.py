import pandas as pd, numpy as np, sys
sys.path.insert(0, '.')

# --- Rwanda convergence precision: bootstrap over the 9 competency domains ---
al = pd.read_csv('outputs/alignment_scores.csv')
conv = pd.read_csv('outputs/au_convergence/au_convergence.csv')

au = al[al.country == 'African Union'].set_index('competency_id')['similarity_score']
def z(s):
    sd = s.std(ddof=0)
    return (s - s.mean())/sd if sd else s*0.0

au_z = z(au)

print("=== Convergence r, with bootstrap over 9 domains (10k resamples) ===")
rng = np.random.default_rng(42)
rows = []
for c in sorted(al.country.unique()):
    if c == 'African Union': continue
    s = al[al.country == c].set_index('competency_id')['similarity_score']
    s_z = z(s)
    r_obs = float(np.corrcoef(s_z.values, au_z.values)[0,1])
    bs = []
    for _ in range(10000):
        idx = rng.integers(0, 9, 9)
        a, b = s_z.values[idx], au_z.values[idx]
        if a.std() == 0 or b.std() == 0: continue
        bs.append(np.corrcoef(a, b)[0,1])
    lo, hi = np.percentile(bs, [2.5, 97.5])
    rows.append({'country': c, 'r': round(r_obs,3), 'lo95': round(lo,3),
                 'hi95': round(hi,3), 'width': round(hi-lo,3)})
res = pd.DataFrame(rows).sort_values('r', ascending=False)
print(res.to_string(index=False))
print("\nNOTE: n=9 domains; bootstrap resamples domains, so it reflects")
print("uncertainty from the small number of domains, not from passage sampling.")
