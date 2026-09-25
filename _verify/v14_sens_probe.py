import pandas as pd, numpy as np, glob, os, sys, json
sys.path.insert(0, '.')
from src import config

# Cached per-country chunk embeddings -> recompute alignment at various top fractions
comp = np.load(config.COMPETENCY_EMBEDDINGS_NPY)
print("competency embeddings:", comp.shape)

chunks = pd.read_csv('outputs/strategy_chunks.csv')
comp_ids = pd.read_csv('data/who_strategy/competencies.csv')
print("competency ids:", comp_ids['competency_id'].tolist()[:12])
print("competencies cols:", comp_ids.columns.tolist())

files = sorted(glob.glob('outputs/embeddings/*_chunk_embeddings.npy'))
print("cached embedding files:", len(files))
