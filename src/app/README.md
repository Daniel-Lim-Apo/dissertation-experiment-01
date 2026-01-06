# App Service

## Overview

FastAPI service that processes text using Ollama LLM for summarization and stores embeddings in Qdrant.

## Purpose

- Generates text summaries using Ollama LLM
- Creates embeddings for both original text and summaries
- Stores vectors in Qdrant collections

## Files

- **main.py**: FastAPI application with text processing endpoints
- **Dockerfile**: Container definition
- **requirements.txt**: Python dependencies

## API Endpoints

- `GET /`: Service status
- `GET /health`: Health check
- `POST /process_text/`: Process text and generate summary

## Collections

- `textos_originais`: Original text embeddings
- `resumos`: Summary embeddings

## Dependencies

- Ollama (LLM service)
- Qdrant (vector database)
