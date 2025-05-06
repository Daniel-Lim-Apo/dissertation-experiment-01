#!/usr/bin/env python
import sys
import warnings

import os
import uuid
import logging
from typing import Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams
import httpx

from crew import PrivacyRareEventCrew


# ------------------- Configuration -------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# LLM_MODEL = os.getenv("LLM_MODEL", "llama3")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-minilm")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))

qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
app = FastAPI()


warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

@app.get("/")
async def root():
    return {"message": "API is running. Use /health or /process_text"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/process_text/")
# async def process_text(data: TextData):
async def process_text():
    try:
        # summary = await generate_summary(data.text)
        # emb_text = await generate_embedding(data.text)
        # emb_summary = await generate_embedding(summary)

        # upsert_to_qdrant("textos_originais", data.text, emb_text, data.metadata)
        # upsert_to_qdrant("resumos", summary, emb_summary, data.metadata)

        # return {"resumo": summary, "mensagem": "Processado com sucesso"}
        print("Running...")
        run()
        return {"resumo": "summary", "mensagem": "Processado com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    inputs = {
        'topic': 'Bananas'
    }
    PrivacyRareEventCrew().crew().kickoff(inputs=inputs)


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "Bananas"
    }
    try:
        PrivacyRareEventCrew().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        PrivacyRareEventCrew().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        PrivacyRareEventCrew().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")
