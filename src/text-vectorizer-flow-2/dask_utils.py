from dask.distributed import Client
from sentence_transformers import SentenceTransformer
import numpy as np

# Connect to Dask cluster
client = Client("tcp://daskscheduler:8786")

# Load model globally to share across workers
model = SentenceTransformer("all-MiniLM-L6-v2")

def vectorize_text(text):
    return model.encode(text, normalize_embeddings=True).tolist()
