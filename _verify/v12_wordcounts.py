import pandas as pd, numpy as np, os, glob, sys
sys.path.insert(0, '.')

# --- Table 1: actual word counts vs manuscript ---
ms = {
 'Benin':15342, "Côte d'Ivoire":15189, 'Egypt':24893, 'Ghana':28514,
 'Kenya':25228, 'Mauritius':25205, 'Morocco':13307, 'Nigeria':22619,
 'Rwanda':4646, 'Senegal':44363, 'South Africa':23522, 'Zimbabwe':20748,
 'African Union':22159,
}
files = {
 'Benin':'benin_ai.txt', "Côte d'Ivoire":'cote_divoire_ai.txt', 'Egypt':'egypt_ai.txt',
 'Ghana':'ghana_ai.txt','Kenya':'kenya_ai.txt','Mauritius':'mauritius_ai.txt',
 'Morocco':'morocco_ai.txt','Nigeria':'nigeria_ai.txt','Rwanda':'rwanda_ai.txt',
 'Senegal':'senegal_ai.txt','South Africa':'south_africa_ai.txt',
 'Zimbabwe':'zimbabwe_ai.txt','African Union':'african_union_ai.txt',
}
print("=== TABLE 1 word counts: manuscript vs raw text file ===")
print(f"{'country':16s} {'MS':>7s} {'raw':>7s} {'diff':>8s}")
for c, f in files.items():
    p = f'data/national_strategies/{f}'
    raw = len(open(p, encoding='utf-8', errors='ignore').read().split())
    print(f"{c:16s} {ms[c]:7d} {raw:7d} {raw-ms[c]:+8d}")
