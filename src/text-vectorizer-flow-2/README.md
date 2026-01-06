# Text Vectorizer (Flow 2)

## Overview

Service for converting text to vector embeddings in the secondary experimental flow: Flow-2.

## Purpose

- Generates embeddings for processed text
- Stores vectors in Qdrant
- Integrates with parallel computing pipeline

## Dependencies

- Embedding models
- Qdrant client
- RabbitMQ (for message consumption)
