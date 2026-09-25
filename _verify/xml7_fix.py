import zipfile, shutil, os, sys, hashlib, io
from PIL import Image

MS = ("/Users/j.forrest/Library/CloudStorage/OneDrive-NortheasternUniversity/"
      "Documents/Private Northeastern/08_Research and Scholarship/Projects/"
      "National AI Strategies/Manuscript/"
      "African_AI_strategies_BMJGH_main_manuscript_v1.0-31August2026.docx")

# 1) REVERT the two Figure 1 caption edits — the embedded Figure 1 image is a
#    z-score heatmap with a separate anchor row, so the ORIGINAL wording was right.
REVERTS = [
    ("yellow indicates above-average and dark purple below-average emphasis",
     "red indicates above-average and blue below-average emphasis"),
    ("Rows are in alphabetical order, with the African Union strategy, "
     "scored on the same scale, shown first as a regional anchor.",
     "Rows are ordered by overall engagement, and the African Union strategy, "
     "scored on the same scale, is shown as a separate anchor row."),
]

# 2) Replace the stale Figure 2 image with the corrected 12-country render.
NEW_FIG2 = 'outputs/figures_for_manuscript/Figure2.png'

z = zipfile.ZipFile(MS)
xml = z.read('word/document.xml').decode('utf-8')
new_fig2 = open(NEW_FIG2, 'rb').read()

print("=== revert checks ===")
for old, new in REVERTS:
    print(f"  present {xml.count(old)} x -> restoring {new[:50]!r}")
    if xml.count(old) != 1:
        print("ABORT: revert target not unique"); sys.exit(1)

for old, new in REVERTS:
    xml = xml.replace(old, new, 1)

print("\n=== Figure 2 image swap ===")
old_bytes = z.read('word/media/image2.png')
print(f"  old: {len(old_bytes):,}B  md5={hashlib.md5(old_bytes).hexdigest()[:12]}")
print(f"  new: {len(new_fig2):,}B  md5={hashlib.md5(new_fig2).hexdigest()[:12]}")
im = Image.open(io.BytesIO(new_fig2)); print(f"  new dims: {im.size}")

tmp = MS + ".tmp"
with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as out:
    for item in z.infolist():
        data = z.read(item.filename)
        if item.filename == 'word/document.xml':
            data = xml.encode('utf-8')
        elif item.filename == 'word/media/image2.png':
            data = new_fig2
        out.writestr(item, data)
z.close()
shutil.move(tmp, MS)
print("\nWROTE:", os.path.basename(MS), os.path.getsize(MS), "bytes")
