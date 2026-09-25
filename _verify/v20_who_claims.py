import pandas as pd, numpy as np, sys
sys.path.insert(0, '.')

al = pd.read_csv('outputs/alignment_scores.csv')
mat = al.pivot(index='country', columns='competency_id', values='similarity_score')
nat = mat.drop('African Union')

def z(s):
    sd = s.std(ddof=0); return (s-s.mean())/sd if sd else s*0.0
Z = nat.apply(z, axis=0)   # z within competency across countries

names = {'C1':'Leadership/governance','C2':'Investment/ops','C3':'Services/scale-up',
         'C4':'Integration/sustainability','C5':'Standards/interop','C6':'Infrastructure',
         'C7':'Health workforce','C8':'Legislation/ethics','C9':'People-centred'}
Zc = Z.rename(columns=names)

print("=== Claim: 'workforce among the two LEAST-emphasised in 10 of 12' ===")
cnt=0; cnt2=0
for c in Zc.index:
    row = Zc.loc[c].sort_values()
    two_least = list(row.index[:2])
    if 'Health workforce' in two_least: cnt+=1
    if 'Health workforce' in list(row.index[:1]): cnt2+=1
    print(f"{c:16s} least2 = {two_least}")
print(f"-> workforce in bottom-2 for {cnt} of 12 countries")
print(f"-> workforce the single LOWEST for {cnt2} of 12")

print("\n=== Claim: 'services/scale-up among two least in 6 of 12' ===")
c3=0
for c in Zc.index:
    two_least = list(Zc.loc[c].sort_values().index[:2])
    if 'Services/scale-up' in two_least: c3+=1
print(f"-> services in bottom-2 for {c3} of 12 countries")

print("\n=== Claim: 'infrastructure, investment and governance MOST emphasised' ===")
for col in ['Infrastructure','Investment/ops','Leadership/governance']:
    ranks = Zc[col].rank(ascending=False)
    print(f"{col:26s} mean rank {ranks.mean():.1f} (1=highest)")

print("\n=== Claim: 'legislation/ethics the main point of differentiation' ===")
spread = Zc.std().sort_values(ascending=False)
print(spread.round(3).to_string())
print("\n=== Claim: 'South Africa and Nigeria emphasise C8 most strongly' ===")
print(Zc['Legislation/ethics'].sort_values(ascending=False).round(2).to_string())

print("\n=== Claim: 'Rwanda lowest overall textual engagement' ===")
print(Z.mean(axis=1).sort_values().round(3).to_string())
print("\n=== African Union anchor: peaks C8, weakest C7 and C3 ===")
auz = z(mat.loc['African Union']).rename(names)
print(auz.sort_values(ascending=False).round(3).to_string())
