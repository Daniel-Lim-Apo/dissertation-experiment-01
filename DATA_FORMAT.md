# Dataset Format Specification

## Overview

This document describes the data formats used throughout the experimental pipeline, from the original CSV source to the JSON messages processed by the system.

> [!IMPORTANT]
> **Data Confidentiality**: The original dataset used in this dissertation contains sensitive information and is not publicly available due to privacy and confidentiality requirements. The data structure is documented here to enable synthetic data generation for reproducibility purposes.

## Original Data Source: CSV Format

The original data file is in **CSV (Comma-Separated Values) format**.

> [!IMPORTANT]
> **Data Preparation**: You must prepare your data in the exact same format as [ocorrencias_example.csv](data/ocorrencias_example.csv). The file uses a **semicolon (`;`)** as the delimiter.
>
> In docker-compose.yml the volumes for the containers that ingest the data are mapped to `/data` in the container:
> volumes:
>
> - D:/DockerVolumes/privacy/RareEvents/data:/data
> - D:/DockerVolumes/privacy/RareEvents/output:/output
>
> and they are looking at ocorrencias.csv file (use this name or change it in the docker-compose.yml file and in the codes).

### CSV Data Dictionary

The following table describes the fields required in the CSV file:

| Field        | Type    | Description                                                                                                                           |
| :----------- | :------ | :------------------------------------------------------------------------------------------------------------------------------------ |
| `ano`        | Integer | The year the police occurrence was recorded (e.g., 2020, 2021).                                                                       |
| `unidade`    | Integer | System code for the police unit or station where the occurrence was registered.                                                       |
| `numero`     | Integer | The unique identification number of the police occurrence within that unit and year.                                                  |
| `aditamento` | Integer | Zero for the main occurrence; higher values (1, 2, 3...) indicate subsequent amendments or addendums.                                 |
| `historico`  | Text    | The full narrative text of the police occurrence in Brazilian Portuguese, including facts, fictional person data, and police actions. |

This CSV file serves as the primary data source and is used to feed the processing workflows in the following scenarios:

- **Flow 1 (With LLM AI agents)**: The CSV file is processed by `\dask-csv-worker-flow-1`.
- **Flow 2 (Without LLM AI agents)**: The CSV file is processed using `dask-csv-worker-flow-2`, which handles the CSV ingestion and transformation pipeline.

The CSV file contains the same fields that are later converted to JSON format for processing.

During the ingestion phase, each row from the CSV file is transformed into a JSON message that follows the structure described below.

Both two flows are in conjunction with `daskscheduler` for distributed data processing.

## JSON Input Data Format

The system expects JSON messages with the following structure.

```json
{
  "ano": "2023",
  "unidade": "UNIT-001",
  "numero": "DOC-12345",
  "aditamento": "1",
  "historico": "This is the textual content to be processed and summarized by the AI agents in flow 1 or in the flow 2 as a raw historico data ready to be vectorized without summarization..."
}
```

### Field Descriptions

> [!NOTE]
> The `historico` field contains the **primary textual data** to be processed. The other fields (`ano`, `unidade`, `numero`, `aditamento`) form a **composite key** that uniquely identifies each document and is preserved throughout the pipeline for traceability in your case you can just use a simple key.

| Field        | Type   | Required | Description                                                   |
| ------------ | ------ | -------- | ------------------------------------------------------------- |
| `ano`        | string | Yes      | Year identifier for the document (part of composite key)      |
| `unidade`    | string | Yes      | Unit or organizational identifier (part of composite key)     |
| `numero`     | string | Yes      | Unique document number (part of composite key)                |
| `aditamento` | string | No       | Amendment or addendum identifier (part of composite key)      |
| `historico`  | string | Yes      | **The main textual content to be processed** (can be lengthy) |

## Output Data Format

After AI processing, just in flow 1, the system produces JSON messages with the following structure:

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

| Field                   | Type   | Description                                              |
| ----------------------- | ------ | -------------------------------------------------------- |
| `ano`                   | string | Year identifier (preserved from input)                   |
| `unidade`               | string | Unit identifier (preserved from input)                   |
| `numero`                | string | Document number (preserved from input)                   |
| `aditamento`            | string | Amendment identifier (preserved from input)              |
| `resumo`                | string | AI-generated summary of the `historico` field            |
| `processing-batch`      | string | Batch identifier (timestamp format: YYYY-MM-DD-HH-MM-SS) |
| `processing-time`       | number | Time in seconds to process this specific message         |
| `total-processing-time` | number | Cumulative processing time since batch start             |
