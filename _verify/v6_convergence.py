import pandas as pd, numpy as np
import sys
sys.path.insert(0, '.')

# --- Convergence: replicate Table S1 ---
conv = pd.read_csv('outputs/au_convergence/au_convergence.csv')
print("=== au_convergence.csv ===")
print(conv.columns.tolist())
print(conv.to_string(index=False))

print("\n=== alignment_scores.csv shape ===")
al = pd.read_csv('outputs/alignment_scores.csv')
print(al.columns.tolist(), al.shape)
print(al.groupby('country').size().to_string())

# --- Contributing passage counts under top_frac_mean ---
print("\n=== CONTRIBUTING PASSAGES per country (top_frac_mean, floor=3) ===")
ch = pd.read_csv('outputs/strategy_chunks.csv')
cnt = ch.groupby('country').size()
rows = []
for c, n in cnt.items():
    n_use = max(3, int(round(n * 0.10)))
    rows.append({'country': c, 'total_chunks': n, 'passages_contributing': n_use})
df = pd.DataFrame(rows).sort_values('total_chunks', ascending=False)
print(df.to_string(index=False))
