import pandas as pd, numpy as np, sys, re, os
sys.path.insert(0, '.')
from src import config, preprocess
from src.models import load_embedding_model

raw = open('_verify/dts_raw.txt').read()
clean = preprocess.clean_text(raw)
chunks = preprocess.chunk_text(clean)   # uses config defaults: 150/20/25
print("cleaned words:", len(clean.split()), "| chunks:", len(chunks))

print("\n=== AU DIGITAL TRANSFORMATION STRATEGY term counts ===")
for t in ['interoperab','accredit','certificat','standard','digital health',
          'health workforce','workforce','health','legislation','ethic']:
    print(f"  {t!r}: {len(re.findall(t, clean, flags=re.IGNORECASE))}")

comp = np.load(config.COMPETENCY_EMBEDDINGS_NPY)
comp = comp/np.linalg.norm(comp, axis=1, keepdims=True)
model = load_embedding_model(config.MODEL_NAME)
print("\nbackend:", model.name)
model.fit(chunks)
E = model.encode(chunks); E = E/np.linalg.norm(E, axis=1, keepdims=True)
S = E @ comp.T
k = min(S.shape[0], max(3, int(round(S.shape[0]*0.10))))
print("chunks used per domain (k):", k)
dts = {f'C{j+1}': float(np.sort(S[:,j])[::-1][:k].mean()) for j in range(9)}

au = pd.read_csv('outputs/alignment_scores.csv')
au = au[au.country=='African Union'].set_index('competency_id')['similarity_score']
print("\n=== AU Continental AI Strategy vs AU Digital Transformation Strategy ===")
print(f"{'domain':6s} {'ContAI':>9s} {'DigTrans':>10s} {'diff':>9s}")
for c in [f'C{i}' for i in range(1,10)]:
    print(f"{c:6s} {au[c]:9.4f} {dts[c]:10.4f} {dts[c]-au[c]:+9.4f}")
print(f"\nmean: ContAI {au.mean():.4f} vs DTS {np.mean(list(dts.values())):.4f}")
pd.Series(dts).to_csv('_verify/dts_scores.csv')
