FROM python:3.10-slim

WORKDIR /text_vectorizer

ENV TZ=America/Sao_Paulo

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY consumer.py .
COPY dask_utils.py .

CMD ["python", "consumer.py"]