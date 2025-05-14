import pika
import json
import time
import requests
from datetime import timedelta, datetime

RABBITMQ_HOST = "rabbitmq"
RABBITMQ_USER = "your_user"
RABBITMQ_PASS = "your_strong_password"
INPUT_QUEUE = "original_text_messages"
OUTPUT_QUEUE = "summary_text_messages"
CREWAI_API_URL = "http://appCrewaiMultiAgents:8000/process_text/"  # Docker service name

MAX_IDLE_ATTEMPTS = 6
WAIT_SECONDS = 10

def setup_rabbitmq():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    parameters = pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue=INPUT_QUEUE, durable=True)
    channel.queue_declare(queue=OUTPUT_QUEUE, durable=True)
    return connection, channel

def format_duration(seconds):
    duration = timedelta(seconds=round(seconds))
    days = duration.days
    hours, remainder = divmod(duration.seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{days} days - {hours} hours - {minutes} minutes - {secs} seconds"

def generate_batch_id(start_time: datetime) -> str:
    return start_time.strftime("%Y-%m-%d-%H-%M-%S")

def process_message(body, channel, script_start_time, processing_batch):
    try:
        msg = json.loads(body)
        historico = msg.get("historico")
        if not historico:
            print("Skipping: 'historico' is empty.")
            return

        metadata = {
            "ano": msg.get("ano"),
            "unidade": msg.get("unidade"),
            "numero": msg.get("numero"),
            "aditamento": msg.get("aditamento")
        }

        api_start_time = time.time()
        response = requests.post(
            CREWAI_API_URL,
            json={"text": historico, "metadata": metadata},
            timeout=600
        )
        api_end_time = time.time()
        processing_time = api_end_time - api_start_time

        if response.status_code != 200:
            print(f"Error from CrewAI API: {response.status_code} {response.text}")
            return

        result = response.json()
        summary = result.get("summary")
        if not summary:
            print("No summary returned.")
            return

        total_time = time.time() - script_start_time

        output_msg = {
            "ano": metadata["ano"],
            "unidade": metadata["unidade"],
            "numero": metadata["numero"],
            "aditamento": metadata["aditamento"],
            "resumo": summary,
            "processing-batch": processing_batch,
            "processing-time": round(processing_time, 3),
            "total-processing-time": round(total_time, 3)
        }

        channel.basic_publish(
            exchange='',
            routing_key=OUTPUT_QUEUE,
            body=json.dumps(output_msg, ensure_ascii=False),
            properties=pika.BasicProperties(
                delivery_mode=2,
                content_type='application/json'
            )
        )
        print(f"Processed message for numero={metadata['numero']}")
        print(f"→ API processing time: {round(processing_time, 3)} seconds")
        print(f"→ Total processing time: {round(total_time, 3)} seconds "
              f"({format_duration(total_time)})")

    except Exception as e:
        print(f"Failed to process message: {e}")

def main():
    script_start_time = time.time()
    script_start_dt = datetime.now()
    print(datetime.now())
    processing_batch = generate_batch_id(script_start_dt)

    print(f"Starting processing batch: {processing_batch}")
    connection, channel = setup_rabbitmq()

    idle_attempts = 0

    while idle_attempts < MAX_IDLE_ATTEMPTS:
        method_frame, header_frame, body = channel.basic_get(queue=INPUT_QUEUE, auto_ack=False)

        if method_frame:
            print("\n📥 Message received. Processing...")
            print("\nMessage:", body)
            process_message(body, channel, script_start_time, processing_batch)
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)
            idle_attempts = 0  # reset after success
        else:
            idle_attempts += 1
            print(f"No message. Waiting {WAIT_SECONDS}s... (Attempt {idle_attempts}/{MAX_IDLE_ATTEMPTS})")
            time.sleep(WAIT_SECONDS)

    final_time = time.time() - script_start_time
    print("\n✅ No messages received after max attempts. Exiting.")
    print(f"🕓 Total runtime: {round(final_time, 3)} seconds "
          f"({format_duration(final_time)})")
    connection.close()

if __name__ == "__main__":
    main()
