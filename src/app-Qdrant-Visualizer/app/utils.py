from qdrant_client import QdrantClient
from scipy.sparse import csr_matrix
import numpy as np
import umap
from sklearn.cluster import KMeans

def fetch_and_process_data():
    client = QdrantClient(host="qdrant", port=6333)
    sample_size = 1000
    neighbors_limit = 20

    # Retrieve a sample of point IDs
    scroll_result, _ = client.scroll(
        collection_name="ocorrencias_resumo_collection",
        limit=sample_size,
        with_payload=False,
        with_vectors=False
    )
    ids = [point.id for point in scroll_result]

    # Compute the distance matrix
    result = client.search_matrix_offsets(
        collection_name="ocorrencias_resumo_collection",
        sample=sample_size,
        limit=neighbors_limit
    )

    matrix = csr_matrix((result.scores, (result.offsets_row, result.offsets_col)), shape=(sample_size, sample_size))
    matrix = matrix.maximum(matrix.T)

    umap_model = umap.UMAP(metric="precomputed", n_neighbors=20, n_components=2)
    vectors_2d = umap_model.fit_transform(matrix)

    kmeans = KMeans(n_clusters=10)
    cluster_labels = kmeans.fit_predict(matrix)

    avg_distances = np.array([
        np.mean(matrix[i].data) if len(matrix[i].data) > 0 else 0
        for i in range(matrix.shape[0])
    ])
    outlier_indices = np.argsort(avg_distances)[-10:]

    # Fetch payloads
    points = client.retrieve(
        collection_name="ocorrencias_resumo_collection",
        ids=ids
    )
    payloads = [pt.payload for pt in points]

    return vectors_2d, cluster_labels, outlier_indices, payloads
