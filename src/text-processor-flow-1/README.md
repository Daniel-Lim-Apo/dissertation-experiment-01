# Text Processor Service

## Overview

Service that processes text messages from RabbitMQ, sends them to AI agents for summarization, and publishes results.

## Purpose

- Consumes text messages from RabbitMQ
- Sends text to CrewAI multi-agents for processing
- Publishes summarized results back to RabbitMQ

## Files

- **processor.py**: Main processing logic with comprehensive docstrings
- **Dockerfile**: Container definition
- **requirements.txt**: Dependencies

## Message Flow

1. Reads from `original_text_messages` queue
2. Processes via CrewAI API
3. Publishes to `summary_text_messages` queue

## Dependencies

- RabbitMQ
- CrewAI Multi-Agents service
