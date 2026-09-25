import pandas as pd, numpy as np, sys
sys.path.insert(0, '.')

al = pd.read_csv('outputs/alignment_scores.csv')
mat = al.pivot(index='country', columns='competency_id', values='similarity_score')
nat = mat.drop('African Union')
names = {'C1':'Leadership','C2':'Investment','C3':'Services','C4':'Integration',
         'C5':'Standards','C6':'Infrastructure','C7':'Workforce','C8':'Legislation',
         'C9':'People-centred'}
RAW = nat.rename(columns=names)

print("=== C8 (Legislation/ethics) RAW, all 12 national strategies ===")
print(RAW['Legislation'].sort_values(ascending=False).round(4).to_string())
print("\n-> top-2 are:", list(RAW['Legislation'].sort_values(ascending=False).index[:2]))

print("\n=== Claim: raw band 0.384-0.582, mean 0.472 ===")
print(f"min={al.similarity_score.min():.4f}  max={al.similarity_score.max():.4f}  mean={al.similarity_score.mean():.4f}")
print(f"national-only: min={nat.values.min():.4f} max={nat.values.max():.4f} mean={nat.values.mean():.4f}")

print("\n=== Corpus totals ===")
ch = pd.read_csv('outputs/strategy_chunks.csv')
print("rows in strategy_chunks.csv:", len(ch))
print("unique (country, chunk_id):", len(ch.drop_duplicates(['country','chunk_id'])))
print("distinct chunk_text values:", ch.chunk_text.nunique())
print("sum of per-country counts:", ch.groupby('country').size().sum())
print("manuscript says 2,489")
