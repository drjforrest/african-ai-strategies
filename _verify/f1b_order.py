import pandas as pd, numpy as np
al = pd.read_csv('outputs/alignment_scores.csv')
mat = al.pivot(index='country', columns='competency_id', values='similarity_score')
CID = [f'C{i}' for i in range(1,10)]
nat = mat.loc[[c for c in mat.index if c != 'African Union'], CID]
mu = nat.mean(axis=0); sd = nat.std(axis=0, ddof=0)
Z = (mat - mu) / sd

print("=== ordering key test: mean of within-competency z ===")
ordz = Z[CID].mean(axis=1).sort_values(ascending=False)
for i,c in enumerate(ordz.index,1):
    print(f"  {i:2d}. {c:16s} {ordz[c]:+.4f}")

print("\nEmbedded image order:")
print("  Côte d'Ivoire, Senegal, Benin, Morocco, South Africa, Ghana,")
print("  Kenya, Zimbabwe, Nigeria, Egypt, Mauritius, Rwanda  <-- 12 national rows")
print("  African Union (anchor)  <-- separate bottom row")

print("\n=== match? ===")
embedded = ["Côte d'Ivoire","Senegal","Benin","Morocco","South Africa","Ghana",
            "Kenya","Zimbabwe","Nigeria","Egypt","Mauritius","Rwanda"]
print("  identical:", list(ordz.index) == embedded)
