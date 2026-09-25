import pandas as pd, numpy as np, sys, re, os
sys.path.insert(0, '.')
from src import config, preprocess
from src.models import load_embedding_model

# --- extract the AU Digital Transformation Strategy 2020-2030 ---
pdf = 'data/AU_strategy/The Digital Transformation Strategy for Africa 2020-2030.pdf'
print("PDF exists:", os.path.exists(pdf), os.path.getsize(pdf))

import pdfplumber
txt = []
with pdfplumber.open(pdf) as d:
    print("pages:", len(d.pages))
    for p in d.pages:
        t = p.extract_text() or ''
        txt.append(t)
raw = "\n".join(txt)
print("raw chars:", len(raw), "words:", len(raw.split()))
open('_verify/dts_raw.txt','w').write(raw)

# clean + chunk with the same pipeline
clean = preprocess.clean_text(raw)
print("cleaned words:", len(clean.split()))
chunks = preprocess.chunk_text(clean, config.CHUNK_SIZE_TOKENS,
                               config.CHUNK_OVERLAP_TOKENS, config.MIN_CHUNK_TOKENS)
print("chunks:", len(chunks))

# term counts on the DTS
print("\n=== AU DIGITAL TRANSFORMATION STRATEGY term counts ===")
for t in ['interoperab','accredit','certificat','standard','digital health',
          'health workforce','workforce','health','legislation','ethic']:
    print(f"  {t!r}: {len(re.findall(t, clean, flags=re.IGNORECASE))}")

# --- run the SAME instrument ---
comp = np.load(config.COMPETENCY_EMBEDDINGS_NPY)
comp = comp/np.linalg.norm(comp, axis=1, keepdims=True)
model = load_embedding_model(config.MODEL_NAME)
print("\nbackend:", model.name)
model.fit(chunks)
E = model.encode(chunks)
E = E/np.linalg.norm(E, axis=1, keepdims=True)
S = E @ comp.T
k = min(S.shape[0], max(3, int(round(S.shape[0]*0.10))))
dts = {f'C{j+1}': np.sort(S[:,j])[::-1][:k].mean() for j in range(9)}

au = pd.read_csv('outputs/alignment_scores.csv')
au = au[au.country=='African Union'].set_index('competency_id')['similarity_score']
print("\n=== AU Continental AI Strategy vs AU Digital Transformation Strategy ===")
print(f"{'domain':5s} {'ContAIStrat':>12s} {'DigTransStrat':>14s} {'diff':>8s}")
for c in [f'C{i}' for i in range(1,10)]:
    print(f"{c:5s} {au[c]:12.4f} {dts[c]:14.4f} {dts[c]-au[c]:+8.4f}")
print("\nmean:", round(au.mean(),4), "vs", round(np.mean(list(dts.values())),4))
