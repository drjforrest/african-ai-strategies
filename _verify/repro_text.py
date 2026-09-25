import re
paras = open('/tmp/ms_text.txt').read().split("\n")
KEY = ['Reproducibility', 'Data availability', 'circularity', 'repository',
       'code', 'permutation', 'Morocco', 'sensitivity', 'bootstrap',
       'prespecified', 'threshold']
seen = set()
for i, p in enumerate(paras):
    if len(p) < 45: continue
    hits = [k for k in KEY if k.lower() in p.lower()]
    if hits and i not in seen:
        seen.add(i)
        print(f"\n[{i}] ({', '.join(hits)})")
        print(p[:1500])
