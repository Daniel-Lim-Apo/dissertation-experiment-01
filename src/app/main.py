from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
from crewai import Agent, Task, Crew, Process, LLM
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams
import uuid
import requests

app = FastAPI()

# LLM local via Ollama
llm = LLM(
    model="ollama/llama3",
    base_url="http://ollama:11434"  # hostname via docker-compose
)

# Qdrant client
qdrant_client = QdrantClient(host="qdrant", port=6333)

# Request model


class TextData(BaseModel):
    text: str
    metadata: Dict[str, str]

# Embedding via Ollama


def generate_embedding(text: str) -> list:
    response = requests.post(
        "http://ollama:11434/api/embeddings",
        json={"model": "all-minilm", "prompt": text}
    )
    if response.status_code == 200:
        return response.json()["embedding"]
    raise Exception("Erro ao gerar embedding.")

# Qdrant insert


def upsert_to_qdrant(collection, text, vector, metadata):
    if not qdrant_client.collection_exists(collection):
        qdrant_client.create_collection(
            collection_name=collection,
            vectors_config=VectorParams(
                size=len(vector), distance=Distance.COSINE)
        )
    point = PointStruct(
        id=str(uuid.uuid4()),
        vector=vector,
        payload={"text": text, **metadata}
    )
    qdrant_client.upsert(collection_name=collection, points=[point])

# API route


@app.post("/process_text/")
async def process_text(data: TextData):
    try:
        # Define agents
        summarizer = Agent(
            role="Resumidor",
            goal="Resumir textos em português.",
            backstory="Especialista em resumo de textos técnicos e científicos.",
            llm=llm
        )

        embedder = Agent(
            role="Gerador de Vetores",
            goal="Gerar embeddings e salvar no Qdrant.",
            backstory="Especialista em NLP vetorial.",
            llm=llm
        )

        # Run summarization
        summary = summarizer.llm.complete(
            f"Resuma o seguinte texto em português:\n\n{data.text}")

        # Embeddings
        emb_text = generate_embedding(data.text)
        emb_summary = generate_embedding(summary)

        # Store in Qdrant
        upsert_to_qdrant("textos_originais", data.text,
                         emb_text, data.metadata)
        upsert_to_qdrant("resumos", summary, emb_summary, data.metadata)

        return {"resumo": summary, "mensagem": "Processado com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
