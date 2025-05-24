import json
import time
import pika
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance, CollectionStatus
from dask import delayed, compute
from sentence_transformers import SentenceTransformer
import uuid
from datetime import timedelta, datetime

MAX_IDLE_ATTEMPTS = 6
WAIT_SECONDS = 10

RABBITMQ_HOST = "rabbitmq"
RABBITMQ_USER = "your_user"
RABBITMQ_PASS = "your_strong_password"
INPUT_QUEUE = "ocorrencias_historico_collection_flow_2"

QDRANT_HOST = "qdrant"
QDRANT_PORT = 6333
QDRANT_COLLECTION = "ocorrencias_historico_vectorized"

qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

model = SentenceTransformer("all-MiniLM-L6-v2")

def vectorize_text(text):
    return model.encode(text, normalize_embeddings=True).tolist()

# Ensure collection exists
def ensure_collection():
    print("[*] Checking or creating Qdrant collection...")
    if QDRANT_COLLECTION not in [c.name for c in qdrant.get_collections().collections]:
        qdrant.recreate_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )
        print(f"[+] Collection '{QDRANT_COLLECTION}' created.")
    else:
        print(f"[✓] Collection '{QDRANT_COLLECTION}' already exists.")

def process_message(msg):
    try:
        data = json.loads(msg)

        ano = data["ano"]
        unidade = data["unidade"]
        numero = data["numero"]
        aditamento = data["aditamento"]
        historico_text = data.get("historico", "")

        # Dask vectorization
        future = delayed(vectorize_text)(historico_text)
        [vectorToSave] = compute(future)
        saveToQdrant(ano, unidade, numero, aditamento, historico_text, vectorToSave)

    except Exception as e:
        print(f"[!] Error processing message: {e}")

def saveToQdrant(ano, unidade, numero, aditamento, historico_text, vectorToSave):
    compound_key = f"{ano}_{unidade}_{numero}_{aditamento}"
    compound_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, compound_key))

    payload = PointStruct(
        id=compound_id,
        vector=vectorToSave,
        payload={
            "ano": ano,
            "unidade": unidade,
            "numero": numero,
            "aditamento": aditamento,
            "historico": historico_text,
        },
    )
    qdrant.upsert(collection_name=QDRANT_COLLECTION, points=[payload])
    print(f"[✓] Saved point {compound_key} to Qdrant with UUID: {compound_id}")

def consume():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOST, credentials=credentials, heartbeat=600
    )

    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue=INPUT_QUEUE, durable=True)

    idle_attempts = 0
    print("[*] Waiting for messages...")

    while idle_attempts < MAX_IDLE_ATTEMPTS:
        method_frame, header_frame, body = channel.basic_get(queue=INPUT_QUEUE)

        if method_frame:
            channel.basic_ack(method_frame.delivery_tag)
            idle_attempts = 0
            print("[>] Message received. Processing...")
            process_message(body.decode())
        else:
            idle_attempts += 1
            print(f"[ ] No message. Waiting {WAIT_SECONDS}s (attempt {idle_attempts}/{MAX_IDLE_ATTEMPTS})")
            time.sleep(WAIT_SECONDS)

    print("[x] Max idle attempts reached. Exiting.")
    connection.close()

if __name__ == "__main__":
    print("=== [START] Vectorization and Qdrant Ingestion Process ===")
    start_time = datetime.now()

    ensure_collection()
    consume()

    end_time = datetime.now()
    elapsed = end_time - start_time
    print(f"=== [END] Process completed in: {str(timedelta(seconds=elapsed.total_seconds()))} ===")
