import pandas as pd, numpy as np, glob, os
print("openpyxl ok")
for f in sorted(glob.glob('data/oxford_readiness_indices/*.xlsx')):
    print("\n===", os.path.basename(f))
    try:
        xl = pd.ExcelFile(f)
        print("sheets:", xl.sheet_names)
        df = pd.read_excel(f, sheet_name=xl.sheet_names[0])
        print("shape:", df.shape)
        print("cols:", df.columns.tolist()[:20])
        s = df.astype(str)
        m = s.apply(lambda c: c.str.contains('Ivoire|Côte|Cote|CÔTE', case=False, na=False)).any(axis=1)
        if m.any():
            print("IVOIRE ROWS:")
            print(df[m].iloc[:, :4].to_string())
        else:
            print("no Ivoire match")
    except Exception as e:
        print("ERR", e)
