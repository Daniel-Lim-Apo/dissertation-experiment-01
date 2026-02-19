import json
import time
import pika
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance, CollectionStatus
from dask import delayed, compute
from sentence_transformers import SentenceTransformer
import uuid

MAX_IDLE_ATTEMPTS = 6
WAIT_SECONDS = 10

RABBITMQ_HOST = "rabbitmq"
RABBITMQ_USER = "your_user"
RABBITMQ_PASS = "your_strong_password"
INPUT_QUEUE = "summary_text_messages"

QDRANT_HOST = "qdrant"
QDRANT_PORT = 6333
QDRANT_COLLECTION = "ocorrencias_resumo_collection"

qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

model = SentenceTransformer("all-MiniLM-L6-v2")

def vectorize_text(text):
    return model.encode(text, normalize_embeddings=True).tolist()

# Ensure collection exists
def ensure_collection():
    if QDRANT_COLLECTION not in [c.name for c in qdrant.get_collections().collections]:
        qdrant.recreate_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )

def process_message(msg):
    try:
        data = json.loads(msg)

        ano = data["ano"]
        unidade = data["unidade"]
        numero = data["numero"]
        aditamento = data["aditamento"]
        resumo_text = data.get("resumo", {}).get("summary", "")

        # Dask vectorization
        future = delayed(vectorize_text)(resumo_text)
        [vectorToSave] = compute(future)
        saveToQdrant(ano, unidade, numero, aditamento, resumo_text, vectorToSave)

    except Exception as e:
        print(f"[!] Error processing message: {e}")

def saveToQdrant(ano, unidade, numero, aditamento, resumo_text, vectorToSave):
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
            "resumo": resumo_text,
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
            process_message(body.decode())
        else:
            idle_attempts += 1
            print(f"[ ] No message. Waiting {WAIT_SECONDS}s (attempt {idle_attempts}/{MAX_IDLE_ATTEMPTS})")
            time.sleep(WAIT_SECONDS)

    print("[x] Max idle attempts reached. Exiting.")
    connection.close()

if __name__ == "__main__":
    ensure_collection()
    consume()
    
    # Dask vectorization for test and debug only
    # text_test = 'Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry s standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum'
    # print('Texto:',text_test)
    # future = delayed(vectorize_text)(text_test)
    # [vectorToSave] = compute(future)
    # print('Vector:',[vectorToSave])
    # # saveToQdrant(ano, unidade, numero, aditamento, vectorToSave)
    # saveToQdrant('0000', '0001', '001', '01', text_test, vectorToSave)
    # print('Saved to QDrant')
    

