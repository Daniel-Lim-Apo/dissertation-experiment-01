import os
import uuid
import logging
from typing import Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment configurations
LLM_MODEL = os.getenv("LLM_MODEL", "ollama/llama3")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-minilm")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))

# Initialize FastAPI app
app = FastAPI()

# Initialize Qdrant client
qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

# Define request model
class TextData(BaseModel):
    text: str
    metadata: Dict[str, str]

# Initialize Qdrant collections at startup
@app.on_event("startup")
async def startup_event():
    try:
        if not qdrant_client.collection_exists("textos_originais"):
            qdrant_client.create_collection(
                collection_name="textos_originais",
                vectors_config=VectorParams(size=384, distance=Distance.COSINE)
            )
            logger.info("Created collection: textos_originais")

        if not qdrant_client.collection_exists("resumos"):
            qdrant_client.create_collection(
                collection_name="resumos",
                vectors_config=VectorParams(size=384, distance=Distance.COSINE)
            )
            logger.info("Created collection: resumos")
    except Exception as e:
        logger.error(f"Error during startup: {e}")

# Asynchronous function to generate embeddings
async def generate_embedding(text: str) -> list:
    url = f"{OLLAMA_URL}/api/embeddings"
    payload = {"model": EMBEDDING_MODEL, "prompt": text}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return response.json()["embedding"]
    except httpx.HTTPError as e:
        logger.error(f"Embedding generation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate embedding.")

# Asynchronous function to generate summary
async def generate_summary(text: str) -> str:
    url = f"{OLLAMA_URL}/api/generate"
    payload = {
        "model": LLM_MODEL,
        "prompt": f"Resuma o seguinte texto em português:\n\n{text}"
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return response.json()["response"]
    except httpx.HTTPError as e:
        logger.error(f"Summary generation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate summary.")

# Function to upsert data into Qdrant
def upsert_to_qdrant(collection: str, text: str, vector: list, metadata: Dict[str, str]):
    try:
        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload={"source_text": text, **metadata}
        )
        qdrant_client.upsert(collection_name=collection, points=[point])
        logger.info(f"Upserted data into collection: {collection}")
    except Exception as e:
        logger.error(f"Failed to upsert data into Qdrant: {e}")
        raise HTTPException(status_code=500, detail="Failed to upsert data into Qdrant.")

# API endpoint to process text
@app.post("/process_text/")
async def process_text(data: TextData):
    try:
        summary = await generate_summary(data.text)
        emb_text = await generate_embedding(data.text)
        emb_summary = await generate_embedding(summary)

        upsert_to_qdrant("textos_originais", data.text, emb_text, data.metadata)
        upsert_to_qdrant("resumos", summary, emb_summary, data.metadata)

        return {"resumo": summary, "mensagem": "Processado com sucesso"}
    except Exception as e:
        logger.error(f"Error processing text: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/")
async def root():
    return {"message": "API is running. Visit /health for status."}
