from fastapi import FastAPI
from fastapi.responses import FileResponse
from utils import analyze_vectors
import os

app = FastAPI()

@app.get("/analyze")
def analyze():
    analyze_vectors("http://qdrant:6333", "ocorrencias_resumo_collection")
    return {"message": "Analysis complete. Use /download/rare or /download/common to get CSVs."}

@app.get("/download/rare")
def download_rare():
    return FileResponse("/app/rare_vectors.csv", filename="rare_vectors.csv")

@app.get("/download/common")
def download_common():
    return FileResponse("/app/common_vectors.csv", filename="common_vectors.csv")
