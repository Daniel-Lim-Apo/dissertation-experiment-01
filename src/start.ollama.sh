#!/bin/sh

set -e

echo ">>> Pulling model: llama3..."
ollama pull llama3

echo ">>> Starting Ollama server..."
exec ollama serve
