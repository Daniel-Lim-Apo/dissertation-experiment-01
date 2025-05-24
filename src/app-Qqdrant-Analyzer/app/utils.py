from qdrant_client import QdrantClient
import numpy as np
import pandas as pd

def analyze_vectors(qdrant_url: str, collection_name: str, k: int = 10, top_n: int = 50):
    client = QdrantClient(
        url=qdrant_url,
        timeout=60.0
    )
    point_ids = []
    offset = None

    # Paginate through all points
    while True:
        result, next_offset = client.scroll(
            collection_name=collection_name,
            with_vectors=False,
            offset=offset,
            limit=1000  # Adjust limit as needed
        )
        point_ids.extend([p.id for p in result])
        if next_offset is None:
            break
        offset = next_offset

    print(f"Total points retrieved: {len(point_ids)}")

    similarities = []

    for pid in point_ids:
        vec = client.retrieve(collection_name, ids=[pid], with_vectors=True)[0].vector
        neighbors = client.search(collection_name, query_vector=vec, limit=k+1)
        neighbors = [n for n in neighbors if n.id != pid]
        avg_sim = np.mean([n.score for n in neighbors]) if neighbors else 0
        similarities.append((pid, avg_sim))

    similarities.sort(key=lambda x: x[1])

    rare = similarities[:top_n]
    common = similarities[-top_n:]

    rare_df = pd.DataFrame(rare, columns=["id", "avg_similarity"])
    common_df = pd.DataFrame(common, columns=["id", "avg_similarity"])

    rare_df.to_csv("/app/rare_vectors.csv", index=False)
    common_df.to_csv("/app/common_vectors.csv", index=False)
