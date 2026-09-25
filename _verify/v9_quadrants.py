import pandas as pd, numpy as np, sys
sys.path.insert(0, '.')

df = pd.read_csv('_verify/corrected_rhetoric_vs_readiness.csv')

def quad(r, w):
    if r >= 0 and w < 0: return 'talk>walk'
    if r < 0 and w >= 0: return 'walk>talk'
    if r >= 0 and w >= 0: return 'aligned-high'
    return 'aligned-low'
df['q'] = [quad(r, w) for r, w in zip(df.rhetoric_z, df.readiness_z)]

print("=== QUADRANT COUNTS: AS PUBLISHED (11 countries, no Cote d'Ivoire) ===")
pub = df[df.country != "Cote d'Ivoire"]
piv = pd.crosstab(pub.country, pub.q)
print(piv.to_string())

print("\n=== South Africa ===")
sa = df[df.country == 'South Africa']
print(sa[['dimension','rhetoric_z','readiness_z','q','text_proximate']].to_string(index=False))
print("aligned-high count:", (sa.q == 'aligned-high').sum(), "of", len(sa))

print("\n=== Egypt & Mauritius: walk>talk on independent dims ===")
for c in ['Egypt', 'Mauritius']:
    sub = df[(df.country == c) & (~df.text_proximate)]
    print(f"{c}: walk>talk {int((sub.q=='walk>talk').sum())} of {len(sub)} independent dims")
    print("   ", sub.q.tolist())

print("\n=== Zimbabwe: aligned-low counts ===")
z = df[df.country == 'Zimbabwe']
print(z[['dimension','q']].to_string(index=False))
print("aligned-low:", (z.q=='aligned-low').sum(), "of", len(z))

print("\n=== Rwanda: independent dims where both high ===")
rw = df[(df.country=='Rwanda') & (~df.text_proximate)]
print(rw[['dimension','rhetoric_z','readiness_z','q']].to_string(index=False))

print("\n=== Nigeria ===")
ng = df[df.country == 'Nigeria']
print(ng[['dimension','rhetoric_z','readiness_z','q','text_proximate']].to_string(index=False))
