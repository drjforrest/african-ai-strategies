import zipfile, os
MS = ("/Users/j.forrest/Library/CloudStorage/OneDrive-NortheasternUniversity/"
      "Documents/Private Northeastern/08_Research and Scholarship/Projects/"
      "National AI Strategies/Manuscript/"
      "African_AI_strategies_BMJGH_main_manuscript_v1.0-31August2026.docx")
z = zipfile.ZipFile(MS)
print("=== word/media/ ===")
for n in z.namelist():
    if n.startswith('word/media/'):
        print(f"  {n}  {z.getinfo(n).file_size:,} bytes")

print("\n=== rels referencing images ===")
rels = z.read('word/_rels/document.xml.rels').decode('utf-8')
import re
for m in re.finditer(r'Id="([^"]+)"[^>]*Target="([^"]*media[^"]*)"', rels):
    print(f"  {m.group(1)} -> {m.group(2)}")

print("\n=== compare with regenerated files ===")
for f in ['Figure1.png','Figure2.png','Figure3.png']:
    p = f'outputs/figures_for_manuscript/{f}'
    print(f"  {f}: {os.path.getsize(p):,} bytes")
