import os, re, zipfile, sys
from xml.etree import ElementTree as ET

MS = ("/Users/j.forrest/Library/CloudStorage/OneDrive-NortheasternUniversity/"
      "Documents/Private Northeastern/08_Research and Scholarship/Projects/"
      "National AI Strategies/Manuscript/"
      "African_AI_strategies_BMJGH_main_manuscript_v1.0-31August2026.docx")
print("exists:", os.path.exists(MS))
print("mtime:", __import__('datetime').datetime.fromtimestamp(os.path.getmtime(MS)))

z = zipfile.ZipFile(MS)
xml = z.read('word/document.xml').decode('utf-8')
ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
root = ET.fromstring(xml)
paras = []
for p in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
    t = "".join(n.text or "" for n in p.iter(
        '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'))
    if t.strip(): paras.append(t.strip())
full = "\n".join(paras)
open('/tmp/ms_text.txt','w').write(full)
print("paras:", len(paras), "chars:", len(full))

# Print paragraphs containing the numbers we care about
KEY = ['r = ', 'permutation', 'p = 0', 'aligned-high', 'seven of nine',
       'of nine', 'of seven', 'convergen', 'Rwanda', 'South Africa',
       'two least', 'most emphasised', 'most emphasized', 'pooled']
print("\n" + "="*70)
for i, p in enumerate(paras):
    if any(k.lower() in p.lower() for k in KEY) and len(p) > 40:
        print(f"\n[{i}] {p}")
