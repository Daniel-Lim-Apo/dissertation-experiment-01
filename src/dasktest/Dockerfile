FROM python:3.10-slim

WORKDIR /app

ENV TZ=America/Sao_Paulo

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY test_dask.py .

CMD ["python", "test_dask.py"]