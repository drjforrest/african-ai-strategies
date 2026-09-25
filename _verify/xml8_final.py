import zipfile, os, hashlib, io
from xml.etree import ElementTree as ET
from PIL import Image

MS = ("/Users/j.forrest/Library/CloudStorage/OneDrive-NortheasternUniversity/"
      "Documents/Private Northeastern/08_Research and Scholarship/Projects/"
      "National AI Strategies/Manuscript/"
      "African_AI_strategies_BMJGH_main_manuscript_v1.0-31August2026.docx")

z = zipfile.ZipFile(MS)
print("zip integrity (None=OK):", z.testzip())
print("parts:", len(z.namelist()))
for n in z.namelist():
    if n.endswith(('.xml', '.rels')):
        ET.fromstring(z.read(n))
print("all XML parses: OK")

print("\n=== embedded media now ===")
for n in sorted(z.namelist()):
    if n.startswith('word/media/'):
        b = z.read(n); im = Image.open(io.BytesIO(b))
        print(f"  {os.path.basename(n):12s} {len(b):>8,}B {im.size} md5={hashlib.md5(b).hexdigest()[:12]}")

xml = z.read('word/document.xml').decode('utf-8')
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
paras = ["".join(t.text or "" for t in p.iter(W+'t'))
         for p in ET.fromstring(xml).iter(W+'p')]
paras = [p.strip() for p in paras if p.strip()]

print("\n=== CAPTIONS (final) ===")
for p in paras:
    if p.startswith(('Figure 1.', 'Figure 2.', 'Figure 3.')):
        print("\n" + p)

full = "\n".join(paras)
print("\n=== CONSISTENCY SCAN ===")
checks = [
    ("r = -0.04 across 108", "corrected pooled stat"),
    ("108 country-by-dimension cells (12 countries)", "corrected cell count"),
    ("99 country-by-dimension", "STALE 99 cells"),
    ("(11 countries)", "STALE 11 countries"),
    ("r = 0.02", "STALE pooled 0.02"),
    ("red indicates above-average", "Fig1 colour wording"),
    ("Rows are ordered by overall engagement", "Fig1 row-order wording"),
    ("r = +0.208", "Table 2 text-prox"),
    ("r = -0.113", "Table 2 independent"),
]
for s, label in checks:
    print(f"  {full.count(s):>3} x  [{label}] {s!r}")
