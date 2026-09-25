import pandas as pd, numpy as np
pd.set_option('display.width', 250)

al = pd.read_csv('outputs/alignment_scores.csv')
mat = al.pivot(index='country', columns='competency_id', values='similarity_score')
CID = [f'C{i}' for i in range(1,10)]
nat = mat.loc[[c for c in mat.index if c != 'African Union'], CID]
au  = mat.loc['African Union', CID]

mu = nat.mean(axis=0); sd = nat.std(axis=0, ddof=0)
Z = (mat - mu) / sd
Z = Z[CID]

# Values read off the embedded Figure 1 image (1 d.p.)
embedded = {
 "Côte d'Ivoire": [1.4,1.4,2.4,2.0,2.1,2.0,2.6,1.9,2.4],
 "Senegal":       [0.1,1.4,0.9,1.0,1.3,1.0,1.0,0.1,0.8],
 "Benin":         [1.5,1.4,1.0,0.5,0.4,-0.0,-0.1,-0.5,0.2],
 "Morocco":       [0.7,-0.2,-0.4,1.1,0.5,1.4,0.3,0.2,0.5],
 "South Africa":  [0.1,0.3,-0.2,-0.2,0.0,0.0,-0.6,1.7,-0.1],
 "Ghana":         [-0.1,-1.0,0.1,0.6,-0.6,0.5,-0.3,-0.7,0.4],
 "Kenya":         [0.1,0.3,-0.1,-0.3,-0.8,-0.3,-0.1,-0.4,-0.0],
 "Zimbabwe":      [0.7,0.1,-0.3,-0.5,-0.2,-0.6,-0.6,-0.3,-0.4],
 "Nigeria":       [-0.6,-0.6,-1.4,-0.6,-0.5,-1.1,-0.5,0.8,-1.3],
 "Egypt":         [-0.6,-0.2,-0.9,-1.2,0.4,-1.1,-1.3,-0.3,-1.5],
 "Mauritius":     [-2.0,-1.0,0.1,-1.2,-1.7,-0.7,0.5,-1.7,0.1],
 "Rwanda":        [-1.5,-1.9,-1.2,-1.3,-1.0,-1.1,-1.0,-0.9,-1.1],
 "African Union": [-0.9,-0.7,-0.7,-1.0,-0.3,-0.6,-0.4,0.0,0.2],
}

print("=== computed z (1dp) vs embedded image ===")
mismatch = 0
for c, exp in embedded.items():
    got = [round(v,1) for v in Z.loc[c, CID].values]
    ok = all(abs(g-e) < 0.06 for g,e in zip(got, exp))
    if not ok: mismatch += 1
    print(f"  {c:16s} {'OK ' if ok else 'DIFF'} got={got}")
    if not ok:
        print(f"  {'':16s}      exp={[round(e,1) for e in exp]}")
print(f"\nmismatches: {mismatch} / 13")

print("\n=== ordering test: mean RAW similarity, descending ===")
order_raw = nat.mean(axis=1).sort_values(ascending=False)
for i,c in enumerate(order_raw.index,1): print(f"  {i:2d}. {c:16s} {order_raw[c]:.4f}")
print("\nEmbedded order: Côte d'Ivoire, Senegal, Benin, Morocco, South Africa, Ghana,")
print("                Kenya, Zimbabwe, Nigeria, Egypt, Mauritius, Rwanda")
