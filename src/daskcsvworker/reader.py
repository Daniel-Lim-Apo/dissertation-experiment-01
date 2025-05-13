import dask.dataframe as dd
from dask.distributed import Client
import os
import dask
import pika
import json

dask.config.set({'dataframe.query-planning': True})

# === RabbitMQ Configuration ===
RABBITMQ_HOST = 'rabbitmq'
RABBITMQ_QUEUE = 'original_text_messages'  # Changed queue name
RABBITMQ_USER = 'your_user'
RABBITMQ_PASS = 'your_strong_password'

def send_message(channel, body):
    """Send a persistent message to RabbitMQ."""
    channel.basic_publish(
        exchange='',
        routing_key=RABBITMQ_QUEUE,
        body=body,
        properties=pika.BasicProperties(
            delivery_mode=2,  # Make message persistent
            content_type='application/json'
        )
    )

def setup_rabbitmq_connection():
    """Establish connection to RabbitMQ and declare the queue."""
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    parameters = pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)  # Durable queue
    return connection, channel

def main():
    client = Client("tcp://daskscheduler:8786")
    print("Connected to Dask scheduler.")

    csv_path = "/data/ocorrencias.csv"
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"File not found: {csv_path}")

    print(f"Reading CSV from {csv_path}")
    df = dd.read_csv(csv_path, sep=';', assume_missing=True)

    print("Columns:", df.columns)
    print("Partition count:", df.npartitions)

    # Count lines in raw CSV
    with open(csv_path, 'r', encoding='utf-8') as f:
        raw_line_count = sum(1 for _ in f) - 1
    print(f"Raw CSV line count (excl. header): {raw_line_count}")

    # Count rows via Dask
    computed_count = df.shape[0].compute()
    print(f"Dask read row count: {computed_count}")

    output_dir = "/output/ocorrencias_parquet"
    os.makedirs(output_dir, exist_ok=True)

    df.to_parquet(output_dir, engine="pyarrow", write_index=False)
    print(f"Data written to {output_dir} in Parquet format.")

    # Read from Parquet
    written_df = dd.read_parquet(output_dir)
    parquet_count = written_df.shape[0].compute()
    print(f"Rows in written Parquet: {parquet_count}")

    if computed_count != parquet_count:
        raise ValueError(f"Row count mismatch: read {computed_count}, written {parquet_count}")

    # === RabbitMQ Integration ===
    connection, channel = setup_rabbitmq_connection()
    print(f"Connected to RabbitMQ. Sending messages to queue '{RABBITMQ_QUEUE}'...")

    # Send each row as a message
    for partition in written_df.to_delayed():
        df_part = partition.compute()
        print()
        for _, row in df_part.iterrows():
            message = json.dumps(row.to_dict(), ensure_ascii=False)
            # print(message)
            send_message(channel, message)

    print("All rows sent to RabbitMQ.")

    connection.close()
    print("RabbitMQ connection closed.")

if __name__ == "__main__":
    main()
