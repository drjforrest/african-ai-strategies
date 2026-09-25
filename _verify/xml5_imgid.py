import zipfile, os, glob, re
from PIL import Image
import io

MSDIR = ("/Users/j.forrest/Library/CloudStorage/OneDrive-NortheasternUniversity/"
         "Documents/Private Northeastern/08_Research and Scholarship/Projects/"
         "National AI Strategies/Manuscript/")
bak = sorted(glob.glob(MSDIR + "*.bak-*"))[-1]
print("backup:", os.path.basename(bak))

os.makedirs('_verify/imgs', exist_ok=True)
for label, path in [("bak", bak),
                    ("cur", MSDIR + "African_AI_strategies_BMJGH_main_manuscript_v1.0-31August2026.docx")]:
    z = zipfile.ZipFile(path)
    for n in z.namelist():
        if n.startswith('word/media/'):
            data = z.read(n)
            fn = f"_verify/imgs/{label}_{os.path.basename(n)}"
            open(fn,'wb').write(data)
            im = Image.open(io.BytesIO(data))
            print(f"  {label} {os.path.basename(n):12s} {len(data):>8,}B  {im.size[0]}x{im.size[1]}  ar={im.size[0]/im.size[1]:.4f}")

print("\n=== regenerated ===")
for f in ['Figure1.png','Figure2.png','Figure3.png']:
    p = f'outputs/figures_for_manuscript/{f}'
    im = Image.open(p)
    print(f"  {f:12s} {os.path.getsize(p):>8,}B  {im.size[0]}x{im.size[1]}  ar={im.size[0]/im.size[1]:.4f}")

# drawing extents in document.xml
z = zipfile.ZipFile(MSDIR + "African_AI_strategies_BMJGH_main_manuscript_v1.0-31August2026.docx")
xml = z.read('word/document.xml').decode('utf-8')
print("\n=== wp:extent (display size, EMU) in document.xml ===")
for i, m in enumerate(re.finditer(r'<wp:extent cx="(\d+)" cy="(\d+)"', xml), 1):
    cx, cy = int(m.group(1)), int(m.group(2))
    print(f"  extent {i}: {cx} x {cy}  ar={cx/cy:.4f}")
