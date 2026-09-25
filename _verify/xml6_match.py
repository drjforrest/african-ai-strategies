import zipfile, os, hashlib, io
from PIL import Image

MS = ("/Users/j.forrest/Library/CloudStorage/OneDrive-NortheasternUniversity/"
      "Documents/Private Northeastern/08_Research and Scholarship/Projects/"
      "National AI Strategies/Manuscript/"
      "African_AI_strategies_BMJGH_main_manuscript_v1.0-31August2026.docx")

def h(b): return hashlib.md5(b).hexdigest()[:12]

z = zipfile.ZipFile(MS)
emb = {n: z.read(n) for n in z.namelist() if n.startswith('word/media/')}
print("=== embedded ===")
for n, b in emb.items():
    im = Image.open(io.BytesIO(b))
    print(f"  {os.path.basename(n):12s} {len(b):>8,}B {im.size} md5={h(b)}")

print("\n=== candidate repo files ===")
cands = [
 'outputs/heatmaps/alignment_heatmap.png',
 'outputs/heatmaps/alignment_heatmap_normalised.png',
 'outputs/heatmaps/clustered_heatmap.png',
 'outputs/figures_for_manuscript/Figure1.png',
 'outputs/figures_for_manuscript/Figure2.png',
 'outputs/figures_for_manuscript/Figure3.png',
 'outputs/rhetoric_vs_readiness/quadrant.png',
 'outputs/rhetoric_vs_readiness/correlation_by_dimension.png',
 'outputs/au_convergence/au_gap_heatmap.png',
]
for c in cands:
    if not os.path.exists(c): print(f"  MISSING {c}"); continue
    b = open(c,'rb').read(); im = Image.open(c)
    match = [k for k,v in emb.items() if h(v)==h(b)]
    print(f"  {os.path.basename(c):38s} {len(b):>8,}B {im.size} md5={h(b)}  MATCHES={match}")
