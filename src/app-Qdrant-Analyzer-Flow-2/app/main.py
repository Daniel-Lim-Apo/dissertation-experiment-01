from fastapi import FastAPI
from fastapi.responses import FileResponse
from qdrant_client import QdrantClient
from dask.distributed import Client
import numpy as np
import pandas as pd
from datetime import datetime

app = FastAPI()

def format_duration(delta):
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{days:02d} Days {hours:02d} Hours {minutes:02d} Minutes {seconds:02d} Seconds"

@app.get("/analyze")
def analyze():
    start_time = datetime.now()
    print(f"Analyze started at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    def print_partial(msg, step_start):
        now = datetime.now()
        partial = now - step_start
        print(f"{msg}")
        print(f"Partial Time: {format_duration(partial)}")

    def compute_avg_similarity(pid, vec, k, collection_name, qdrant_url):
        from qdrant_client import QdrantClient
        import numpy as np
        client = QdrantClient(url=qdrant_url)
        neighbors = client.search(collection_name=collection_name, query_vector=vec, limit=k + 1)
        neighbors = [n for n in neighbors if n.id != pid]
        avg_sim = np.mean([n.score for n in neighbors]) if neighbors else 0
        return (pid, avg_sim)

    step_start = datetime.now()
    print("Connecting to Qdrant...")
    client = QdrantClient(url="http://qdrant:6333")
    print_partial("Connected to Qdrant.", step_start)

    step_start = datetime.now()
    print("Connecting to Dask scheduler...")
    dask_client = Client("tcp://daskscheduler:8786")
    print_partial("Connected to Dask scheduler.", step_start)

    step_start = datetime.now()
    print("Fetching all vectors from Qdrant...")
    all_vectors = {}
    offset = None
    total_count = 0
    while True:
        result, offset = client.scroll(collection_name="ocorrencias_historico_vectorized", with_vectors=True, offset=offset, limit=1000)
        batch_count = len(result)
        total_count += batch_count
        print(f"Retrieved {batch_count} vectors (total so far: {total_count})")
        for point in result:
            all_vectors[point.id] = point.vector
        if offset is None:
            break
    print_partial(f"Total vectors retrieved: {len(all_vectors)}", step_start)

    step_start = datetime.now()
    print("Submitting tasks to Dask workers...")
    futures = [
        dask_client.submit(compute_avg_similarity, pid, vec, 10, "ocorrencias_historico_vectorized", "http://qdrant:6333")
        for pid, vec in all_vectors.items()
    ]
    print_partial("Tasks submitted.", step_start)

    step_start = datetime.now()
    print("Waiting for all tasks to complete...")
    similarities = dask_client.gather(futures)
    print_partial("All tasks completed.", step_start)

    step_start = datetime.now()
    print("Sorting results...")
    similarities.sort(key=lambda x: x[1])
    print_partial("Sorting complete.", step_start)

    step_start = datetime.now()
    print("Saving rare vectors to /app/rare_vectors.csv")
    pd.DataFrame(similarities[:50], columns=["id", "avg_similarity"]).to_csv("/app/rare_vectors.csv", index=False)
    print("Saving common vectors to /app/common_vectors.csv")
    pd.DataFrame(similarities[-50:], columns=["id", "avg_similarity"]).to_csv("/app/common_vectors.csv", index=False)
    print_partial("Files saved.", step_start)

    total_time = datetime.now() - start_time
    print(f"Total Time: {format_duration(total_time)}")

    return {"message": "Analysis complete. Use /download/rare or /download/common to get CSVs."}

@app.get("/download/rare")
def download_rare():
    return FileResponse("/app/rare_vectors.csv", filename="rare_vectors.csv")

@app.get("/download/common")
def download_common():
    return FileResponse("/app/common_vectors.csv", filename="common_vectors.csv")
