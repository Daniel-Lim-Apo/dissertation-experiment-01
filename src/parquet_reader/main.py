import json
import pika
import time
import sys
from pyspark.sql import SparkSession
from pyspark.sql.utils import AnalysisException

PARQUET_PATH = "/shared/ocorrencias_parquet"
QUEUE_NAME = "ocorrencias_historico_to_process"
RABBITMQ_HOST = "rabbitmq"
RABBITMQ_PORT = 5672
BATCH_SIZE = 100
MAX_RETRIES = 5
RETRY_BASE_DELAY = 2  # seconds

def connect_with_retry(max_retries=MAX_RETRIES):
    """Try to establish RabbitMQ connection with exponential backoff."""
    attempt = 0
    while attempt < max_retries:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=RABBITMQ_HOST, port=RABBITMQ_PORT))
            channel = connection.channel()
            channel.queue_declare(queue=QUEUE_NAME, durable=True)
            return connection, channel
        except pika.exceptions.AMQPConnectionError as e:
            delay = RETRY_BASE_DELAY * (2 ** attempt)
            print(f"RabbitMQ connection failed (attempt {attempt + 1}/{max_retries}): {e}")
            print(f"Retrying in {delay} seconds...")
            time.sleep(delay)
            attempt += 1

    print("All RabbitMQ connection attempts failed. Exiting.")
    sys.exit(1)

def send_batch(messages):
    """Send a batch of JSON messages to RabbitMQ with retries."""
    if not messages:
        return

    connection, channel = connect_with_retry()

    for msg in messages:
        try:
            channel.basic_publish(
                exchange='',
                routing_key=QUEUE_NAME,
                body=msg,
                properties=pika.BasicProperties(delivery_mode=2)
            )
        except Exception as e:
            print(f"Failed to send message: {e}")

    connection.close()
    print(f"Sent {len(messages)} messages to RabbitMQ.")

def main():
    print("Starting Spark session...")
    spark = SparkSession.builder \
        .appName("Parquet to RabbitMQ - Streamed w/ Retry") \
        .master("spark://spark-master:7077") \
        .getOrCreate()

    try:
        print(f"Reading Parquet from: {PARQUET_PATH}")
        df = spark.read.parquet(PARQUET_PATH)
    except AnalysisException as e:
        print(f"Failed to read Parquet: {e}")
        return

    print("Streaming rows to RabbitMQ in batches with retry...")

    buffer = []
    count = 0
    for row in df.toLocalIterator():
        json_msg = json.dumps(row.asDict(), ensure_ascii=False)
        buffer.append(json_msg)
        count += 1

        if len(buffer) >= BATCH_SIZE:
            send_batch(buffer)
            buffer = []

    # Final flush
    if buffer:
        send_batch(buffer)

    print(f"Finished. Total messages sent: {count}")

if __name__ == "__main__":
    main()
