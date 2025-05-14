FROM python:3.10-slim

RUN pip install pyspark pika

WORKDIR /parquet_reader

ENV TZ=America/Sao_Paulo

COPY main.py .

CMD ["python", "main.py"]
