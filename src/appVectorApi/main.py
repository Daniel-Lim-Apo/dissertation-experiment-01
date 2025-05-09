from fastapi import FastAPI
from pydantic import BaseModel
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, PointStruct, Distance
# from dask.distributed import Client
import hashlib
from typing import List
from embedding import compute_embedding


app = FastAPI()

# Dask client connection
# client = Client("tcp://daskscheduler:8786")

# Qdrant setup
qdrant = QdrantClient(host="qdrant", port=6333)
COLLECTION_NAME = "text_vectors"
VECTOR_SIZE = 384  # for all-MiniLM-L6-v2

try:
    qdrant.get_collection(COLLECTION_NAME)
except:
    qdrant.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
    )

# Models
class CompoundKey(BaseModel):
    number: str
    place: str
    year: str

class VectorRequest(BaseModel):
    id: CompoundKey
    text: str

class SearchRequestModel(BaseModel):
    text: str
    top_k: int = 5


@app.get("/")
async def root():
    return {"message": "API is running. Use /health or /process_text"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/vectorize")
def vectorize_text(data: VectorRequest):
    # future = client.submit(compute_embedding, data.text)
    # vector = future.result()
    vector = compute_embedding(data.text) 

    key_str = f"{data.id.number}_{data.id.place}_{data.id.year}"
    uid = hashlib.md5((key_str + data.text).encode()).hexdigest()

    point = PointStruct(
        id=uid,
        vector=vector,
        payload={
            "number": data.id.number,
            "place": data.id.place,
            "year": data.id.year,
            "text": data.text
        }
    )
    qdrant.upsert(collection_name=COLLECTION_NAME, points=[point])

    return {"status": "success", "id": uid}

@app.post("/search")
def search_similar(data: SearchRequestModel):
    # future = client.submit(compute_embedding, data.text)
    # query_vector = future.result()
    
    query_vector = compute_embedding(data.text)

    results = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=data.top_k,
        with_payload=True
    )

    return [
        {
            "score": r.score,
            "payload": dict(r.payload) if isinstance(r.payload, dict) else str(r.payload)
        }
        for r in results
    ]

