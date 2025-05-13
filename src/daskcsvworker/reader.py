import dask.dataframe as dd
from dask.distributed import Client
import os
import dask
import pika
import json

dask.config.set({'dataframe.query-planning': True})

RABBITMQ_HOST = 'rabbitmq'
RABBITMQ_QUEUE = 'original_text_messages'
RABBITMQ_USER = 'your_user'
RABBITMQ_PASS = 'your_strong_password'

def send_message(channel, body):
    """Send a persistent message to RabbitMQ."""
    channel.basic_publish(
        exchange='',
        routing_key=RABBITMQ_QUEUE,
        body=body,
        properties=pika.BasicProperties(
            delivery_mode=2,
            content_type='application/json'
        )
    )

def setup_rabbitmq_connection():
    """Establish connection to RabbitMQ and declare the queue."""
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    parameters = pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
    return connection, channel

def main():
    client = Client("tcp://daskscheduler:8786")
    print("Connected to Dask scheduler.")

    csv_path = "/data/ocorrencias.csv"
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"File not found: {csv_path}")

    print(f"Reading CSV from {csv_path}")
    df = dd.read_csv(
        csv_path,
        sep=';',
        dtype={
            "ano": "str",
            "unidade": "str",
            "numero": "str",
            "aditamento": "str",
            "historico": "str"
        },
        assume_missing=True
    )

    output_dir = "/output/ocorrencias_parquet"
    os.makedirs(output_dir, exist_ok=True)

    df.to_parquet(output_dir, engine="pyarrow", write_index=False)
    print(f"Data written to {output_dir} in Parquet format.")

    # Materialize the entire parquet file once
    print("Reading Parquet once into a full Pandas DataFrame to avoid recomputation...")
    full_df = dd.read_parquet(output_dir).compute()
    print(f"Total rows to send: {len(full_df)}")

    connection, channel = setup_rabbitmq_connection()
    print(f"Connected to RabbitMQ. Sending messages to queue '{RABBITMQ_QUEUE}'...")

    for row in full_df.itertuples(index=False):
        # Convert row to dict, then to JSON
        row_dict = row._asdict()
        message = json.dumps(row_dict, ensure_ascii=False)
        send_message(channel, message)

    print("All messages sent successfully.")

    connection.close()
    print("RabbitMQ connection closed.")

if __name__ == "__main__":
    main()
