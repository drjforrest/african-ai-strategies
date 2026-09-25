import pandas as pd, numpy as np, glob, os, sys
sys.path.insert(0, '.')
from src import config
exec(open('_verify/v17_replicate.py').read().split('# --- replicate published')[0])

print("=== CONVERGENCE SENSITIVITY: 5% / 10% / 20% (official metric) ===")
res = {}
for tf in (0.05, 0.10, 0.20):
    res[tf] = conv_metric(align(tf))
df = pd.DataFrame(res)
df['r05'] = df[0.05].rank(ascending=False)
df['r10'] = df[0.10].rank(ascending=False)
df['r20'] = df[0.20].rank(ascending=False)
print(df.sort_values('r10').round(3).to_string())
print("\nRwanda at each threshold:", {f"{int(k*100)}%": round(df.loc['Rwanda', k],3) for k in res})
print("Spearman 5% vs 10%:", round(df[0.05].corr(df[0.10], method='spearman'),3))
print("Spearman 10% vs 20%:", round(df[0.10].corr(df[0.20], method='spearman'),3))
print("Spearman 5% vs 20%:", round(df[0.05].corr(df[0.20], method='spearman'),3))
print("\nTop-3 membership by threshold:")
for k in res:
    print(f"  {int(k*100)}%: {list(df[k].sort_values(ascending=False).head(3).index)}")
print("Bottom-3 membership by threshold:")
for k in res:
    print(f"  {int(k*100)}%: {list(df[k].sort_values().head(3).index)}")
df.to_csv('_verify/aggregation_sensitivity.csv')

# --- Bootstrap CI on convergence r (resample 9 domains) ---
print("\n=== BOOTSTRAP 95% CI on convergence r (official metric, 10%) ===")
long = align(0.10)
mat = long.pivot_table(index='country', columns='competency_id', values='score', aggfunc='first')[CID]
countries = [c for c in mat.index if c != 'African Union']
mu = mat.loc[countries].mean(axis=0); sd = mat.loc[countries].std(axis=0, ddof=0).replace(0,1.0)
z = (mat-mu)/sd
a = z.loc['African Union', CID].to_numpy(float)
rng = np.random.default_rng(7)
rows=[]
for c in countries:
    v = z.loc[c, CID].to_numpy(float)
    def r_of(vv, aa):
        vc, ac = vv-vv.mean(), aa-aa.mean()
        return float(vc@ac/(np.linalg.norm(vc)*np.linalg.norm(ac)))
    obs = r_of(v, a)
    bs=[]
    for _ in range(20000):
        i = rng.integers(0,9,9)
        vv, aa = v[i], a[i]
        if vv.std()==0 or aa.std()==0: continue
        bs.append(r_of(vv,aa))
    lo,hi = np.percentile(bs,[2.5,97.5])
    rows.append({'country':c,'r':round(obs,3),'lo95':round(lo,3),'hi95':round(hi,3),'width':round(hi-lo,3)})
out = pd.DataFrame(rows).sort_values('r',ascending=False)
print(out.to_string(index=False))
out.to_csv('_verify/convergence_bootstrap_ci.csv')
