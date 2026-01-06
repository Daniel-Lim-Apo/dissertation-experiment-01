# CrewAI Multi-Agents Service

## Overview

Multi-agent AI system using CrewAI framework to process and summarize textual data with specialized agents.

## Purpose

- Orchestrates multiple AI agents for text analysis
- Provides structured summarization using agent collaboration
- Integrates with Ollama for LLM capabilities

## Structure

- **main.py**: FastAPI application exposing agent processing
- **crew.py**: CrewAI agent and task definitions
- **config/**: Agent and task configurations
- **tools/**: Custom tools for agents
- **utils/**: Utility functions

## API Endpoints

- `POST /process_text/`: Process text using AI agent crew

## Dependencies

- CrewAI framework
- Ollama (LLM backend)
