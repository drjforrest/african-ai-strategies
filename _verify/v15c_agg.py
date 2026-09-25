import pandas as pd, numpy as np, glob, os, sys
sys.path.insert(0, '.')
from src import config

comp = np.load(config.COMPETENCY_EMBEDDINGS_NPY)
comp = comp / np.linalg.norm(comp, axis=1, keepdims=True)

name_map = {
 'african_union':'African Union','benin':'Benin','cote_divoire':"Côte d'Ivoire",
 'egypt':'Egypt','ghana':'Ghana','kenya':'Kenya','mauritius':'Mauritius',
 'morocco':'Morocco','nigeria':'Nigeria','rwanda':'Rwanda','senegal':'Senegal',
 'south_africa':'South Africa','zimbabwe':'Zimbabwe',
}

def align(top_frac, floor=3):
    rows = []
    for f in sorted(glob.glob('outputs/embeddings/*_chunk_embeddings.npy')):
        stem = os.path.basename(f).replace('_chunk_embeddings.npy','').replace('_ai','')
        E = np.load(f); E = E/np.linalg.norm(E, axis=1, keepdims=True)
        S = E @ comp.T
        n = S.shape[0]; k = min(n, max(floor, int(round(n*top_frac))))
        for j in range(9):
            rows.append({'country': name_map[stem], 'competency_id': f'C{j+1}',
                         'score': np.sort(S[:,j])[::-1][:k].mean(), 'k': k})
    return pd.DataFrame(rows)

def z(s):
    sd = s.std(ddof=0)
    return (s - s.mean())/sd if sd else s*0.0

out = {}
for tf in (0.05, 0.10, 0.20):
    a = align(tf)
    piv = a.pivot_table(index='country', columns='competency_id', values='score', aggfunc='first')
    au = piv.loc['African Union']
    res = {c: float(np.corrcoef(z(piv.loc[c]).values, z(au).values)[0,1])
           for c in piv.index if c != 'African Union'}
    out[tf] = res
    print(f"\n-- top {int(tf*100)}% -- (Rwanda k={a[a.country=='Rwanda'].k.iloc[0]}, "
          f"Senegal k={a[a.country=='Senegal'].k.iloc[0]})")
    for c, v in sorted(res.items(), key=lambda kv: -kv[1]):
        print(f"   {c:16s} {v:+.3f}")

df = pd.DataFrame(out)
df['r05']=df[0.05].rank(ascending=False); df['r10']=df[0.10].rank(ascending=False)
df['r20']=df[0.20].rank(ascending=False)
print("\n=== RANK STABILITY ===")
print(df.sort_values('r10').round(3).to_string())
print("\nSpearman 5% vs 10%:", round(df[0.05].corr(df[0.10], method='spearman'),3))
print("Spearman 10% vs 20%:", round(df[0.10].corr(df[0.20], method='spearman'),3))
df.to_csv('_verify/aggregation_sensitivity.csv')
