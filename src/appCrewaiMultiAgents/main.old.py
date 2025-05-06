import os
import uuid
import logging
from typing import Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams
import httpx

# ------------------- Configuration -------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

LLM_MODEL = os.getenv("LLM_MODEL", "llama3")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-minilm")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))

qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
app = FastAPI()

# ------------------- Models -------------------

class TextData(BaseModel):
    text: str
    metadata: Dict[str, str]

# ------------------- Startup -------------------

@app.on_event("startup")
async def startup_event():
    try:
        for name in ["textos_originais", "resumos"]:
            if not qdrant_client.collection_exists(name):
                qdrant_client.create_collection(
                    collection_name=name,
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
                )
                logger.info(f"Created collection: {name}")
    except Exception as e:
        logger.error(f"Startup error: {e}")

# ------------------- Utility Functions -------------------

async def generate_embedding(text: str) -> list:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/embeddings",
                json={"model": EMBEDDING_MODEL, "prompt": text}
            )
            response.raise_for_status()
            return response.json()["embedding"]
    except Exception as e:
        logger.error(f"Embedding error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate embedding.")

async def generate_summary(text: str) -> str:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={"model": LLM_MODEL, "prompt": f"Resuma o seguinte texto:\n\n{text}"}
            )
            response.raise_for_status()
            return response.json()["response"]
    except Exception as e:
        logger.error(f"Summary error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate summary.")

def upsert_to_qdrant(collection: str, text: str, vector: list, metadata: Dict[str, str]):
    try:
        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload={"source_text": text, **metadata}
        )
        qdrant_client.upsert(collection_name=collection, points=[point])
        logger.info(f"Upserted into {collection}")
    except Exception as e:
        logger.error(f"Qdrant error: {e}")
        raise HTTPException(status_code=500, detail="Failed to upsert to Qdrant.")

# ------------------- Routes -------------------

@app.get("/")
async def root():
    return {"message": "API is running. Use /health or /process_text"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/process_text/")
async def process_text(data: TextData):
    try:
        summary = await generate_summary(data.text)
        emb_text = await generate_embedding(data.text)
        emb_summary = await generate_embedding(summary)

        upsert_to_qdrant("textos_originais", data.text, emb_text, data.metadata)
        upsert_to_qdrant("resumos", summary, emb_summary, data.metadata)

        return {"resumo": summary, "mensagem": "Processado com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")

# @app.on_event("startup")
# async def startup_event():
#     for attempt in range(20):
#         try:
#             for name in ["textos_originais", "resumos"]:
#                 if not qdrant_client.collection_exists(name):
#                     qdrant_client.create_collection(
#                         collection_name=name,
#                         vectors_config=VectorParams(size=384, distance=Distance.COSINE)
#                     )
#                     logger.info(f"Created collection: {name}")
#             break  # Success
#         except Exception as e:
#             logger.error(f"Startup attempt {attempt + 1}: {e}")
#             await asyncio.sleep(5)  # wait before retrying
#     else:
#         logger.error("Qdrant not available after multiple attempts.")
#         raise RuntimeError("Failed to connect to Qdrant.")