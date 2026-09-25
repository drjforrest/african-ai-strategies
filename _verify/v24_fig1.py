import pandas as pd
al = pd.read_csv('outputs/alignment_scores.csv')
p = al.pivot(index='country', columns='competency_id', values='similarity_score')
print("pivot index order:", list(p.index))
print("alphabetical?", list(p.index) == sorted(p.index))
print("\nmean by country (desc = overall engagement):")
print(p.mean(axis=1).sort_values(ascending=False).round(4).to_string())
print("\nFigure 1 cmap is 'viridis' (yellow=high, dark purple=low), not red/blue.")
print("AU is first row (index 0), NOT a separate bottom anchor row.")
