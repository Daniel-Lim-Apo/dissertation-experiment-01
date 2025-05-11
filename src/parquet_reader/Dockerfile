FROM python:3.10-slim

RUN pip install pyspark pika

WORKDIR /parquet_reader
COPY main.py .

CMD ["python", "main.py"]
