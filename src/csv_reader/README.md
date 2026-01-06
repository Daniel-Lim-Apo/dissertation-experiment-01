# CSV Reader Service

## Overview

Apache Spark-based service for reading CSV files and converting them to Parquet format.

## Purpose

- Reads large CSV datasets using Spark
- Converts CSV to Parquet for efficient storage
- Handles UTF-8 encoded data

## Files

- **main.py**: Spark application for CSV to Parquet conversion
- **Dockerfile**: Container definition
- **requirements.txt**: Dependencies

## Usage

Reads from `/shared/data/` and writes to `/shared/output/`
