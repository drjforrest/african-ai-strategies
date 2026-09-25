import zipfile, re, os, sys
MS = ("/Users/j.forrest/Library/CloudStorage/OneDrive-NortheasternUniversity/"
      "Documents/Private Northeastern/08_Research and Scholarship/Projects/"
      "National AI Strategies/Manuscript/"
      "African_AI_strategies_BMJGH_main_manuscript_v1.0-31August2026.docx")

z = zipfile.ZipFile(MS)
print("=== parts ===")
for n in z.namelist():
    if n.startswith('word/') and n.endswith('.xml'):
        print(" ", n, z.getinfo(n).file_size)

xml = z.read('word/document.xml').decode('utf-8')
print("\ndocument.xml chars:", len(xml))

# locate the two target caption phrases inside the raw XML
targets = [
    "red indicates above-average and blue below-average emphasis",
    "Rows are ordered by overall engagement",
    "The pooled correlation is r = 0.02 across 99",
]
for t in targets:
    i = xml.find(t)
    print(f"\n=== {t[:55]!r} -> idx {i} ===")
    if i > 0:
        print(xml[max(0,i-400):i+len(t)+200])
