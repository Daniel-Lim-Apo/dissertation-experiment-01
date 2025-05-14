FROM python:3.10-slim

# Set working directory
WORKDIR /daskscheduler

ENV TZ=America/Sao_Paulo

# Copy requirements from local build context
COPY requirements.txt .

# Install all dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Optional: add diagnostics
RUN pip list

# Run Dask scheduler
CMD ["dask-scheduler"]
