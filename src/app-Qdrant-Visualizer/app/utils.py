from qdrant_client import QdrantClient
from scipy.sparse import csr_matrix
import numpy as np
import umap
from sklearn.cluster import KMeans

def fetch_and_process_data():
    client = QdrantClient(host="qdrant", port=6333)

    # Step 1: Fetch all point metadata
    all_points, _ = client.scroll(
        collection_name="ocorrencias_resumo_collection",
        with_payload=False,
        with_vectors=False,
        limit=10000  # Assume less than 10k points for simplicity
    )

    # Step 2: Sort by ID and extract list of sorted IDs
    sorted_ids = sorted(point.id for point in all_points)
    sample_size = len(sorted_ids)

    # Step 3: Compute distance matrix based on sorted IDs
    result = client.search_matrix_offsets(
        collection_name="ocorrencias_resumo_collection",
        sample=sample_size,
        limit=20
    )

    matrix = csr_matrix(
        (result.scores, (result.offsets_row, result.offsets_col)),
        shape=(sample_size, sample_size)
    )
    matrix = matrix.maximum(matrix.T)

    # Step 4: Apply UMAP and clustering
    umap_model = umap.UMAP(metric="precomputed", n_neighbors=20, n_components=2, random_state=42)
    vectors_2d = umap_model.fit_transform(matrix)

    kmeans = KMeans(n_clusters=50, random_state=42)
    cluster_labels = kmeans.fit_predict(matrix)

    # Step 5: Compute average neighbor distances to detect outliers
    avg_distances = np.array([
        np.mean(matrix[i].data) if len(matrix[i].data) > 0 else 0
        for i in range(matrix.shape[0])
    ])
    outlier_indices = np.argsort(avg_distances)[-10:]

    # Step 6: Fetch payloads for sorted IDs
    points = client.retrieve(
        collection_name="ocorrencias_resumo_collection",
        ids=sorted_ids
    )
    payloads = [pt.payload for pt in points]

    return vectors_2d, cluster_labels, outlier_indices, payloads
