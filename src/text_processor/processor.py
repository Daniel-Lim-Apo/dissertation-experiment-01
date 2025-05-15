import pika
import json
import time
import requests
from datetime import timedelta, datetime
import traceback
import sys

RABBITMQ_HOST = "rabbitmq"
RABBITMQ_USER = "your_user"
RABBITMQ_PASS = "your_strong_password"
INPUT_QUEUE = "original_text_messages"
OUTPUT_QUEUE = "summary_text_messages"
CREWAI_API_URL = "http://appCrewaiMultiAgents:8000/process_text/"

MAX_IDLE_ATTEMPTS = 6
WAIT_SECONDS = 10
MAX_RETRIES = 5
RETRY_DELAY = 5  # seconds

def log(msg: str):
    print(f"[{datetime.now().isoformat()}] {msg}", flush=True)

def setup_rabbitmq():
    attempt = 0
    while attempt < MAX_RETRIES:
        try:
            credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
            parameters = pika.ConnectionParameters(
                host=RABBITMQ_HOST,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()

            # Declare queues (can be extended with DLQ bindings)
            channel.queue_declare(queue=INPUT_QUEUE, durable=True)
            channel.queue_declare(queue=OUTPUT_QUEUE, durable=True)

            log("✅ Connected to RabbitMQ.")
            return connection, channel
        except Exception as e:
            log(f"[!] Failed to connect to RabbitMQ: {e}")
            attempt += 1
            time.sleep(RETRY_DELAY)
    raise RuntimeError("❌ Could not establish RabbitMQ connection after retries.")

def format_duration(seconds):
    duration = timedelta(seconds=round(seconds))
    days = duration.days
    hours, remainder = divmod(duration.seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{days}d {hours}h {minutes}m {secs}s"

def generate_batch_id(start_time: datetime) -> str:
    return start_time.strftime("%Y-%m-%d-%H-%M-%S")

def process_message(body, script_start_time, processing_batch):
    msg = json.loads(body)
    historico = msg.get("historico")
    if not historico:
        log("⚠️ Skipping message: 'historico' is empty.")
        return None

    metadata = {
        "ano": msg.get("ano"),
        "unidade": msg.get("unidade"),
        "numero": msg.get("numero"),
        "aditamento": msg.get("aditamento")
    }

    try:
        api_start_time = time.time()
        response = requests.post(
            CREWAI_API_URL,
            json={"text": historico, "metadata": metadata},
            timeout=600
        )
        api_end_time = time.time()
        processing_time = api_end_time - api_start_time

        if response.status_code != 200:
            log(f"❌ CrewAI API error: {response.status_code} - {response.text}")
            return None

        result = response.json()
        summary = result.get("summary")
        if not summary:
            log("⚠️ CrewAI response missing 'summary'.")
            return None

        total_time = time.time() - script_start_time

        return {
            "ano": metadata["ano"],
            "unidade": metadata["unidade"],
            "numero": metadata["numero"],
            "aditamento": metadata["aditamento"],
            "resumo": summary,
            "processing-batch": processing_batch,
            "processing-time": round(processing_time, 3),
            "total-processing-time": round(total_time, 3)
        }

    except Exception as e:
        log(f"🔥 Exception during API call: {e}")
        traceback.print_exc(file=sys.stdout)
        return None

def main():
    script_start_time = time.time()
    processing_batch = generate_batch_id(datetime.now())
    log(f"🚀 Starting processing batch: {processing_batch}")

    try:
        connection, channel = setup_rabbitmq()
    except Exception as e:
        log(str(e))
        return

    idle_attempts = 0

    while idle_attempts < MAX_IDLE_ATTEMPTS:
        try:
            method_frame, header_frame, body = channel.basic_get(queue=INPUT_QUEUE, auto_ack=False)

            if method_frame:
                log("📥 Message received. Processing...")
                result = process_message(body, script_start_time, processing_batch)

                if result:
                    channel.basic_publish(
                        exchange='',
                        routing_key=OUTPUT_QUEUE,
                        body=json.dumps(result, ensure_ascii=False),
                        properties=pika.BasicProperties(
                            delivery_mode=2,
                            content_type='application/json'
                        )
                    )
                    log(f"✅ Processed and published: {result['numero']}")
                else:
                    log("⚠️ Processing failed. Message will be re-queued or dead-lettered.")

                # Acknowledge if still valid
                if channel.is_open:
                    channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                else:
                    log("⚠️ Skipping ack: channel was closed mid-processing.")

                idle_attempts = 0
            else:
                idle_attempts += 1
                log(f"⏳ No message. Sleeping {WAIT_SECONDS}s (attempt {idle_attempts}/{MAX_IDLE_ATTEMPTS})")
                time.sleep(WAIT_SECONDS)

        except pika.exceptions.AMQPConnectionError as conn_err:
            log(f"🔌 Lost RabbitMQ connection: {conn_err}")
            try:
                connection, channel = setup_rabbitmq()
                idle_attempts = 0
            except Exception as e:
                log(f"❌ Reconnection failed: {e}")
                break

        except Exception as e:
            log(f"🔥 Unexpected error: {e}")
            traceback.print_exc(file=sys.stdout)

    final_time = time.time() - script_start_time
    log("🛑 No new messages. Exiting.")
    log(f"🕓 Runtime: {round(final_time, 3)}s ({format_duration(final_time)})")

    try:
        connection.close()
    except:
        pass

if __name__ == "__main__":
    main()
