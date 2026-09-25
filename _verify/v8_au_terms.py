import pandas as pd, re, sys
sys.path.insert(0, '.')

def counts(path, terms, label):
    txt = open(path, encoding='utf-8', errors='ignore').read()
    words = len(txt.split())
    print(f"\n=== {label} ({words:,} words) ===")
    for t in terms:
        n = len(re.findall(t, txt, flags=re.IGNORECASE))
        print(f"  {t!r}: {n}")

au = 'data/national_strategies/african_union_ai.txt'
terms = ['standard', 'interoperab', 'accredit', 'certificat', 'curricul',
         'health workforce', 'workforce', 'health', 'legislation', 'ethic',
         'conformity assessment', 'data protection', 'digital health']
counts(au, terms, "AU Continental AI Strategy")

# AU Digital Transformation Strategy (2020-2030) - the comparison claim
import subprocess, os
print("\n=== AU Digital Transformation Strategy ===")
dh = 'data/AU_strategy/The Digital Transformation Strategy for Africa 2020-2030.pdf'
print("exists:", os.path.exists(dh))
