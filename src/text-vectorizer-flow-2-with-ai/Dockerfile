FROM python:3.10-slim

WORKDIR /text-vectorizer-flow-2-With-AI

ENV TZ=America/Sao_Paulo

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY consumer.py .
COPY dask_utils.py .

CMD ["python", "consumer.py"]