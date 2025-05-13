#!/bin/sh
set -e

echo ">>> Starting Ollama server..."
exec ollama serve
