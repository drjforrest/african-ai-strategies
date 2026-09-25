import pandas as pd, numpy as np, itertools, sys
sys.path.insert(0, '.')

def pearson(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) < 3 or a.std() == 0 or b.std() == 0: return np.nan
    return float(np.corrcoef(a, b)[0, 1])
def z(s):
    sd = s.std(ddof=0)
    return (s - s.mean())/sd if sd else s*0.0

DIM_MAP = {
    "GOV_VISION":("Vision","Government",True),
    "GOV_GOVERNANCE":("Governance and Ethics","Government",True),
    "GOV_DIGITAL_CAPACITY":("Digital Capacity","Government",False),
    "GOV_ADAPTABILITY":("Adaptability","Government",False),
    "TECH_MATURITY":("Maturity","Technology Sector",False),
    "TECH_INNOVATION":("Innovation Capacity","Technology Sector",False),
    "TECH_HUMAN_CAPITAL":("Human Capital","Technology Sector",False),
    "DATA_INFRASTRUCTURE":("Infrastructure","Data and Infrastructure",False),
    "DATA_AVAILABILITY":("Data Availability","Data and Infrastructure",False),
}
rhet = pd.read_csv('outputs/reference_alignment/oxford_dimensions_2021_2024_embed/'
                   'oxford_dimensions_2021_2024_embed_alignment_scores.csv')
rhet = rhet[rhet.competency_id.isin(DIM_MAP)].copy()
rhet['dimension'] = rhet.competency_id.map(lambda c: DIM_MAP[c][0])
rhet = rhet.rename(columns={'similarity_score':'rhetoric_raw'})[['country','dimension','rhetoric_raw']]
rhet['country'] = rhet['country'].replace({"Côte d'Ivoire":"Cote d'Ivoire"})

panel = pd.read_csv('data/oxford_readiness_indices/processed/oxford_panel_2021_2024_tidy.csv')
dims = panel[panel.level=='dimension']
meas = dims[dims.year.astype(str)=='2024'][['country','metric','score']].rename(
    columns={'metric':'dimension','score':'readiness_raw'})

df = rhet.merge(meas, on=['country','dimension'], how='inner')
df['text_proximate'] = df.dimension.map(lambda d: next(v[2] for v in DIM_MAP.values() if v[0]==d))
df['rhetoric_z'] = df.groupby('dimension')['rhetoric_raw'].transform(z)
df['readiness_z'] = df.groupby('dimension')['readiness_raw'].transform(z)
def quad(r,w):
    if r>=0 and w<0: return 'talk>walk'
    if r<0 and w>=0: return 'walk>talk'
    if r>=0 and w>=0: return 'aligned-high'
    return 'aligned-low'
df['q'] = [quad(r,w) for r,w in zip(df.rhetoric_z, df.readiness_z)]

for label, sub in [("AS PUBLISHED (11 countries)", df[df.country!="Cote d'Ivoire"]),
                   ("CORRECTED (12 countries)", df)]:
    print(f"\n########## {label} ##########")
    for c in ['South Africa','Egypt','Mauritius','Zimbabwe','Rwanda','Nigeria']:
        s = sub[sub.country==c]
        ind = s[~s.text_proximate]
        print(f"{c:14s} aligned-high {int((s.q=='aligned-high').sum())}/9 | "
              f"indep walk>talk {int((ind.q=='walk>talk').sum())}/{len(ind)} | "
              f"indep talk>walk {int((ind.q=='talk>walk').sum())}/{len(ind)} | "
              f"aligned-low {int((s.q=='aligned-low').sum())}/9")
