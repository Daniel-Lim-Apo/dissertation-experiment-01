# Dask Test Service

## Overview

This is a simple test service to verify the Dask distributed cluster connectivity and functionality.

## Purpose

- **Validates** that the Dask scheduler and workers are properly configured
- **Tests** distributed task execution across the cluster
- **Demonstrates** basic parallel computing with Dask

## Contents

### Files

- **[test_dask.py](test_dask.py)**: Main test script that connects to the Dask cluster and submits parallel tasks
- **[Dockerfile](Dockerfile)**: Container definition for the test service
- **[requirements.txt](requirements.txt)**: Python dependencies (`dask[distributed]`)

### How It Works

> [!IMPORTANT]
> **Prerequisites**: The Dask scheduler (`daskscheduler`) and at least one Dask worker must be running and online before executing this test. The test will fail if it cannot connect to the scheduler.

The test script:

1. Connects to the Dask scheduler at `tcp://daskscheduler:8786`
2. Submits 10 parallel tasks using `client.submit()`
3. Each task simulates a 15-second computation (`slow_increment` function)
4. Gathers and prints the results

## Running the Test

### Via Docker Compose

```bash
docker-compose up dasktest
```

### Expected Output

```
Connected to Dask cluster
Results: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
```

The tasks should complete in approximately 15 seconds (not 150 seconds) if parallel execution is working correctly across multiple workers.

## Use Case

This service is used during development and deployment to:

- Verify Dask cluster health
- Test network connectivity between services
- Validate that workers are accepting and processing tasks
- Benchmark parallel execution performance
