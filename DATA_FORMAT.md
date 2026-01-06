# Dataset Format Specification

## Overview

This document describes the expected JSON format for input data used in the experimental pipeline. 

> [!IMPORTANT]
> **Data Confidentiality**: The original dataset used in this dissertation contains sensitive information and is not publicly available due to privacy and confidentiality requirements. The data structure is documented here to enable synthetic data generation for reproducibility purposes.

## Input Data Format

The system expects JSON messages with the following structure:

```json
{
  "ano": "2023",
  "unidade": "UNIT-001",
  "numero": "DOC-12345",
  "aditamento": "1",
  "historico": "This is the textual content to be processed and summarized by the AI agents..."
}
```

### Field Descriptions

> [!NOTE]
> The `historico` field contains the **primary textual data** to be processed by the AI agents. The other fields (`ano`, `unidade`, `numero`, `aditamento`) form a **composite key** that uniquely identifies each document and is preserved throughout the pipeline for traceability in your case you can just use a simple key.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ano` | string | Yes | Year identifier for the document (part of composite key) |
| `unidade` | string | Yes | Unit or organizational identifier (part of composite key) |
| `numero` | string | Yes | Unique document number (part of composite key) |
| `aditamento` | string | No | Amendment or addendum identifier (part of composite key) |
| `historico` | string | Yes | **The main textual content to be processed** (can be lengthy) |

## Output Data Format

After processing, the system produces JSON messages with the following structure:

```json
{
  "ano": "2023",
  "unidade": "UNIT-001",
  "numero": "DOC-12345",
  "aditamento": "1",
  "resumo": "AI-generated summary of the original text...",
  "processing-batch": "2024-01-06-15-30-00",
  "processing-time": 12.345,
  "total-processing-time": 45.678
}
```

### Output Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `ano` | string | Year identifier (preserved from input) |
| `unidade` | string | Unit identifier (preserved from input) |
| `numero` | string | Document number (preserved from input) |
| `aditamento` | string | Amendment identifier (preserved from input) |
| `resumo` | string | AI-generated summary of the `historico` field |
| `processing-batch` | string | Batch identifier (timestamp format: YYYY-MM-DD-HH-MM-SS) |
| `processing-time` | number | Time in seconds to process this specific message |
| `total-processing-time` | number | Cumulative processing time since batch start |


