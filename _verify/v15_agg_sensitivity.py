import pandas as pd, numpy as np, glob, os, sys, itertools
sys.path.insert(0, '.')
from src import config
from src import competencies as C

comp = np.load(config.COMPETENCY_EMBEDDINGS_NPY)          # (9, 384)
comp = comp / np.linalg.norm(comp, axis=1, keepdims=True)
chunks = pd.read_csv('outputs/strategy_chunks.csv')
counts = chunks.groupby('country').size().to_dict()

def align(top_frac, floor=3):
    rows = []
    for f in sorted(glob.glob('outputs/embeddings/*_chunk_embeddings.npy')):
        name = os.path.basename(f).replace('_chunk_embeddings.npy', '')
        E = np.load(f)
        E = E / np.linalg.norm(E, axis=1, keepdims=True)
        S = E @ comp.T                                     # (n_chunks, 9)
        n = S.shape[0]
        k = max(floor, int(round(n * top_frac)))
        k = min(k, n)
        for j in range(9):
            col = np.sort(S[:, j])[::-1][:k]
            rows.append({'country': name, 'competency_id': f'C{j+1}',
                         'score': col.mean(), 'k': k})
    return pd.DataFrame(rows)

def z(s):
    sd = s.std(ddof=0)
    return (s - s.mean())/sd if sd else s*0.0

# name -> display map
name_map = {
 'african_union':'African Union','benin':'Benin','cote_divoire':"Côte d'Ivoire",
 'egypt':'Egypt','ghana':'Ghana','kenya':'Kenya','mauritius':'Mauritius',
 'morocco':'Morocco','nigeria':'Nigeria','rwanda':'Rwanda','senegal':'Senegal',
 'south_africa':'South Africa','zimbabwe':'Zimbabwe',
}

print("=== AGGREGATION SENSITIVITY: convergence ranking at 5% / 10% / 20% ===")
out = {}
for tf in (0.05, 0.10, 0.20):
    a = align(tf)
    a['country'] = a['country'].map(name_map)
    piv = a.pivot(index='country', columns='competency_id', values='score')
    au = piv.loc['African Union']
    res = {}
    for c in piv.index:
        if c == 'African Union': continue
        x, y = z(piv.loc[c]), z(au)
        res[c] = float(np.corrcoef(x.values, y.values)[0,1])
    out[tf] = res
    print(f"\n-- top {int(tf*100)}% --  (Rwanda k={a[a.country=='Rwanda'].k.iloc[0]}, "
          f"Senegal k={a[a.country=='Senegal'].k.iloc[0]})")
    for c, v in sorted(res.items(), key=lambda kv: -kv[1]):
        print(f"   {c:16s} {v:+.3f}")

# rank stability
print("\n=== RANK STABILITY across thresholds ===")
df = pd.DataFrame(out)
df['rank5']  = df[0.05].rank(ascending=False)
df['rank10'] = df[0.10].rank(ascending=False)
df['rank20'] = df[0.20].rank(ascending=False)
print(df.sort_values('rank10').round(3).to_string())
print("\nSpearman rank corr 5% vs 10%:", round(df[0.05].corr(df[0.10], method='spearman'),3))
print("Spearman rank corr 10% vs 20%:", round(df[0.10].corr(df[0.20], method='spearman'),3))
df.to_csv('_verify/aggregation_sensitivity.csv')
print("\nwrote _verify/aggregation_sensitivity.csv")
