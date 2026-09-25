import pandas as pd, numpy as np, itertools, sys
sys.path.insert(0, '.')

def pearson(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) < 3 or a.std() == 0 or b.std() == 0: return np.nan
    return float(np.corrcoef(a, b)[0, 1])

DIM_MAP = {
    "GOV_VISION":          ("Vision", "Government", True),
    "GOV_GOVERNANCE":      ("Governance and Ethics", "Government", True),
    "GOV_DIGITAL_CAPACITY":("Digital Capacity", "Government", False),
    "GOV_ADAPTABILITY":    ("Adaptability", "Government", False),
    "TECH_MATURITY":       ("Maturity", "Technology Sector", False),
    "TECH_INNOVATION":     ("Innovation Capacity", "Technology Sector", False),
    "TECH_HUMAN_CAPITAL":  ("Human Capital", "Technology Sector", False),
    "DATA_INFRASTRUCTURE": ("Infrastructure", "Data and Infrastructure", False),
    "DATA_AVAILABILITY":   ("Data Availability", "Data and Infrastructure", False),
}

rhet = pd.read_csv('outputs/reference_alignment/oxford_dimensions_2021_2024_embed/'
                   'oxford_dimensions_2021_2024_embed_alignment_scores.csv')
rhet = rhet[rhet.competency_id.isin(DIM_MAP)].copy()
rhet['dimension'] = rhet.competency_id.map(lambda c: DIM_MAP[c][0])
rhet = rhet.rename(columns={'similarity_score': 'rhetoric_raw'})[['country','dimension','rhetoric_raw']]

panel = pd.read_csv('data/oxford_readiness_indices/processed/oxford_panel_2021_2024_tidy.csv')
dims = panel[panel.level == 'dimension'].copy()
meas = dims[dims.year.astype(str) == '2024'][['country','metric','score']].copy()
meas = meas.rename(columns={'metric':'dimension','score':'readiness_raw'})

def z(s):
    sd = s.std(ddof=0)
    return (s - s.mean())/sd if sd else s*0.0

def build(rhet_df, meas_df):
    df = rhet_df.merge(meas_df, on=['country','dimension'], how='inner')
    df['text_proximate'] = df.dimension.map(lambda d: next(v[2] for v in DIM_MAP.values() if v[0]==d))
    df['pillar'] = df.dimension.map(lambda d: next(v[1] for v in DIM_MAP.values() if v[0]==d))
    df['rhetoric_z'] = df.groupby('dimension')['rhetoric_raw'].transform(z)
    df['readiness_z'] = df.groupby('dimension')['readiness_raw'].transform(z)
    return df

# ACCENT-FOLD FIX
rhet_fixed = rhet.copy()
rhet_fixed['country'] = rhet_fixed['country'].replace({"Côte d'Ivoire": "Cote d'Ivoire"})

df_fixed = build(rhet_fixed, meas)
print("=== CORRECTED (Cote d'Ivoire restored via accent fold) ===")
print("countries:", df_fixed.country.nunique(), "cells:", len(df_fixed))
print(sorted(df_fixed.country.unique()))

per = (df_fixed.groupby(['dimension','text_proximate'])
       .apply(lambda g: pearson(g.rhetoric_raw, g.readiness_raw), include_groups=False)
       .reset_index(name='r').sort_values('r'))
print("\n", per.to_string(index=False))
tp = per[per.text_proximate]['r'].mean()
ind = per[~per.text_proximate]['r'].mean()
print(f"\ntext-proximate mean r = {tp:+.4f}")
print(f"independent   mean r = {ind:+.4f}")
print(f"pooled r = {pearson(df_fixed.rhetoric_z, df_fixed.readiness_z):+.4f}")

dims_list = sorted(df_fixed.dimension.unique())
rb = per.set_index('dimension')['r'].to_dict()
c=t=0
for combo in itertools.combinations(dims_list,2):
    t+=1
    if np.mean([rb[x] for x in combo]) >= tp - 1e-12: c+=1
print(f"permutation p = {c/t:.4f} ({c} of {t})")

# also excluding Morocco on corrected set
d2 = df_fixed[df_fixed.country != 'Morocco']
per2 = (d2.groupby(['dimension','text_proximate'])
        .apply(lambda g: pearson(g.rhetoric_raw, g.readiness_raw), include_groups=False)
        .reset_index(name='r'))
tp2 = per2[per2.text_proximate]['r'].mean(); ind2 = per2[~per2.text_proximate]['r'].mean()
rb2 = per2.set_index('dimension')['r'].to_dict(); c2=t2=0
for combo in itertools.combinations(dims_list,2):
    t2+=1
    if np.mean([rb2[x] for x in combo]) >= tp2 - 1e-12: c2+=1
print(f"\n=== CORRECTED, excl. Morocco (n={d2.country.nunique()}) ===")
print(f"text-proximate mean r = {tp2:+.4f}; independent mean r = {ind2:+.4f}; p = {c2/t2:.4f}")
print(per2.to_string(index=False))

df_fixed.to_csv('_verify/corrected_rhetoric_vs_readiness.csv', index=False)
print("\nwrote _verify/corrected_rhetoric_vs_readiness.csv")
