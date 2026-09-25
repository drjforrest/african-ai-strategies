import zipfile, os
from xml.etree import ElementTree as ET
MS = ("/Users/j.forrest/Library/CloudStorage/OneDrive-NortheasternUniversity/"
      "Documents/Private Northeastern/08_Research and Scholarship/Projects/"
      "National AI Strategies/Manuscript/"
      "African_AI_strategies_BMJGH_main_manuscript_v1.0-31August2026.docx")

# 1. zip integrity
z = zipfile.ZipFile(MS)
bad = z.testzip()
print("zip testzip (None = OK):", bad)
print("parts:", len(z.namelist()))

# 2. XML well-formedness for every xml part
for n in z.namelist():
    if n.endswith('.xml') or n.endswith('.rels'):
        try:
            ET.fromstring(z.read(n))
        except Exception as e:
            print("  XML ERROR", n, e)
print("all XML parts parse: OK")

# 3. read back the captions
xml = z.read('word/document.xml').decode('utf-8')
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
root = ET.fromstring(xml)
paras = []
for p in root.iter(W+'p'):
    t = "".join(n.text or "" for n in p.iter(W+'t'))
    if t.strip(): paras.append(t.strip())

print("\n=== FIGURE CAPTIONS AFTER EDIT ===")
for p in paras:
    if p.startswith(('Figure 1.', 'Figure 2.', 'Figure 3.')):
        print("\n" + p)

# 4. confirm no stale values remain anywhere
print("\n=== STALE-VALUE SCAN ===")
full = "\n".join(paras)
for s in ["r = 0.02 across 99", "99 country-by-dimension", "(11 countries)",
          "red indicates above-average", "Rows are ordered by overall engagement"]:
    print(f"  {full.count(s)} x  {s!r}")
