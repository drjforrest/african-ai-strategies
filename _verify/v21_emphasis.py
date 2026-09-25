import pandas as pd, numpy as np, sys
sys.path.insert(0, '.')
pd.set_option('display.width', 200)

al = pd.read_csv('outputs/alignment_scores.csv')
mat = al.pivot(index='country', columns='competency_id', values='similarity_score')
nat = mat.drop('African Union')
names = {'C1':'Leadership','C2':'Investment','C3':'Services','C4':'Integration',
         'C5':'Standards','C6':'Infrastructure','C7':'Workforce','C8':'Legislation',
         'C9':'People-centred'}

def z(s):
    sd = s.std(ddof=0); return (s-s.mean())/sd if sd else s*0.0
Z = nat.apply(z, axis=0).rename(columns=names)
RAW = nat.rename(columns=names)

def bottom2(df, label):
    print(f"\n########## {label} ##########")
    w=0; s=0
    for c in df.index:
        r = df.loc[c].sort_values()
        b2 = list(r.index[:2])
        if 'Workforce' in b2: w+=1
        if 'Services' in b2: s+=1
        print(f"  {c:16s} bottom2={str(b2):45s} top2={list(r.index[-2:])}")
    print(f"  -> Workforce in bottom-2: {w}/{len(df)}")
    print(f"  -> Services  in bottom-2: {s}/{len(df)}")

bottom2(Z, "STANDARDISED (z within competency, across countries)")
bottom2(RAW, "RAW cosine scores")

print("\n########## MEAN WITHIN-COUNTRY RANK (1 = most emphasised) ##########")
for label, df in [("z", Z), ("raw", RAW)]:
    ranks = df.rank(axis=1, ascending=False)
    print(f"\n-- {label} --")
    print(ranks.mean().sort_values().round(2).to_string())

print("\n########## VARIANCE ACROSS COUNTRIES (differentiation), RAW ##########")
print(RAW.std().sort_values(ascending=False).round(4).to_string())
print("\n########## VARIANCE, z ##########")
print(Z.std().sort_values(ascending=False).round(3).to_string())
