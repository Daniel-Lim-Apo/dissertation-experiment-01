# Dask CSV Reader (Flow 2)

## Overview

Dask-based service for parallel CSV reading and processing in the secondary experimental flow: Flow-2.

## Purpose

- Reads CSV files using Dask for parallel processing
- Handles large datasets efficiently
- Publishes data to RabbitMQ for downstream processing

## Dependencies

- Dask distributed
- RabbitMQ client
- Pandas
