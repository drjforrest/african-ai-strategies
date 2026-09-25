import glob, os, numpy as np, pandas as pd
for f in sorted(glob.glob('outputs/embeddings/*.npy')):
    print(os.path.basename(f), np.load(f).shape)
ch = pd.read_csv('outputs/strategy_chunks.csv')
print("\nchunks per country:")
print(ch.groupby('country').size().to_string())
