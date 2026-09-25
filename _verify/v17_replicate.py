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
CID = [f'C{i}' for i in range(1,10)]

def align(top_frac, floor=3):
    rows = []
    for f in sorted(glob.glob('outputs/embeddings/*_chunk_embeddings.npy')):
        stem = os.path.basename(f).replace('_chunk_embeddings.npy','').replace('_ai','')
        E = np.load(f); E = E/np.linalg.norm(E, axis=1, keepdims=True)
        S = E @ comp.T
        n = S.shape[0]; k = min(n, max(floor, int(round(n*top_frac))))
        for j in range(9):
            rows.append({'country': name_map[stem], 'competency_id': CID[j],
                         'score': np.sort(S[:,j])[::-1][:k].mean(), 'k': k})
    return pd.DataFrame(rows)

def conv_metric(long, anchor='African Union'):
    """Exactly the official script's metric."""
    mat = long.pivot_table(index='country', columns='competency_id',
                           values='score', aggfunc='first')[CID]
    countries = [c for c in mat.index if c != anchor]
    mu = mat.loc[countries].mean(axis=0)
    sd = mat.loc[countries].std(axis=0, ddof=0).replace(0, 1.0)
    z = (mat - mu) / sd
    a = z.loc[anchor, CID].to_numpy(float)
    out = {}
    for c in countries:
        v = z.loc[c, CID].to_numpy(float)
        vc, ac = v - v.mean(), a - a.mean()
        out[c] = float(vc @ ac / (np.linalg.norm(vc)*np.linalg.norm(ac)))
    return out

# --- replicate published 10% result ---
long10 = align(0.10)
pub = pd.read_csv('outputs/au_convergence/au_convergence.csv').set_index('country')['profile_r_to_AU']
rep = conv_metric(long10)
print("=== REPLICATION CHECK (10%) ===")
print(f"{'country':16s} {'published':>10s} {'replicated':>11s} {'diff':>8s}")
for c in pub.index:
    print(f"{c:16s} {pub[c]:10.3f} {rep[c]:11.3f} {rep[c]-pub[c]:+8.3f}")
