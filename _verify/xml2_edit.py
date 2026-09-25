import zipfile, shutil, os, sys, datetime

MS = ("/Users/j.forrest/Library/CloudStorage/OneDrive-NortheasternUniversity/"
      "Documents/Private Northeastern/08_Research and Scholarship/Projects/"
      "National AI Strategies/Manuscript/"
      "African_AI_strategies_BMJGH_main_manuscript_v1.0-31August2026.docx")

EDITS = [
    # --- Figure 1: colour scale is viridis, not red/blue ---
    ("red indicates above-average and blue below-average emphasis",
     "yellow indicates above-average and dark purple below-average emphasis"),
    # --- Figure 1: rows are alphabetical; AU is first, not a bottom anchor ---
    ("Rows are ordered by overall engagement, and the African Union strategy, "
     "scored on the same scale, is shown as a separate anchor row.",
     "Rows are in alphabetical order, with the African Union strategy, "
     "scored on the same scale, shown first as a regional anchor."),
    # --- Figure 2: pooled statistic after the Côte d'Ivoire join correction ---
    ("The pooled correlation is r = 0.02 across 99 country-by-dimension cells "
     "(11 countries).",
     "The pooled correlation is r = -0.04 across 108 country-by-dimension cells "
     "(12 countries)."),
]

z = zipfile.ZipFile(MS)
xml = z.read('word/document.xml').decode('utf-8')
original = xml

print("=== PRE-EDIT OCCURRENCE COUNTS ===")
ok = True
for old, new in EDITS:
    n = xml.count(old)
    print(f"  {n} x  {old[:60]!r}")
    if n != 1:
        ok = False
if not ok:
    print("\nABORT: every target must appear exactly once.")
    sys.exit(1)

for old, new in EDITS:
    xml = xml.replace(old, new, 1)

print("\n=== POST-EDIT VERIFICATION ===")
for old, new in EDITS:
    print(f"  old gone: {xml.count(old) == 0}   new present: {xml.count(new) == 1}")

if len(xml) == len(original):
    print("\nABORT: length unchanged — edits did not apply.")
    sys.exit(1)
print(f"  length {len(original)} -> {len(xml)} ({len(xml)-len(original):+d})")

# --- repack, preserving every other part byte-for-byte ---
tmp = MS + ".tmp"
with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as out:
    for item in z.infolist():
        data = z.read(item.filename)
        if item.filename == 'word/document.xml':
            data = xml.encode('utf-8')
        out.writestr(item, data)
z.close()
shutil.move(tmp, MS)
print("\nWROTE:", MS)
print("size:", os.path.getsize(MS))
