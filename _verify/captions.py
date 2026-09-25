import re
full = open('/tmp/ms_text.txt').read()
paras = full.split("\n")

print("=== ALL FIGURE / TABLE CAPTIONS ===")
for i, p in enumerate(paras):
    if re.match(r'^(Figure|Table)\s', p.strip()):
        print(f"\n[{i}] {p.strip()}")

print("\n\n=== PARAGRAPHS MENTIONING r = OR CELL COUNTS ===")
for i, p in enumerate(paras):
    if re.search(r'r\s*=\s*[-+]?0\.|cells|country-by-dimension', p):
        print(f"\n[{i}] {p.strip()}")
