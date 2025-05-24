from qdrant_client import QdrantClient
from sklearn.metrics import pairwise_distances
from sklearn.manifold import trustworthiness
from scipy.sparse import csr_matrix
import numpy as np
import umap
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns

def fetch_and_process_data(save_image_path=None):
    client = QdrantClient(host="qdrant", port=6333)

    # Step 1: Scroll to get all points with vectors and payloads
    all_points = []
    next_page = None
    while True:
        batch, next_page = client.scroll(
            collection_name="ocorrencias_resumo_collection",
            limit=1000,
            offset=next_page,
            with_payload=True,
            with_vectors=True
        )
        all_points.extend(batch)
        if next_page is None:
            break

    # Step 2: Sort by ID for consistency
    all_points.sort(key=lambda p: p.id)
    vectors = np.array([pt.vector for pt in all_points])
    payloads = [pt.payload for pt in all_points]
    sample_size = vectors.shape[0]

    # Step 3: Compute full cosine distance matrix
    print("Computing full cosine distance matrix...")
    dist_matrix = pairwise_distances(vectors, metric="cosine")
    matrix = csr_matrix(dist_matrix)

    # Step 4: UMAP projection
    umap_model = umap.UMAP(
        metric="precomputed",
        n_neighbors=30,
        min_dist=0.05,
        random_state=42
    )
    vectors_2d = umap_model.fit_transform(matrix)

    # Step 5: KMeans clustering
    kmeans = KMeans(n_clusters=50, random_state=42)
    cluster_labels = kmeans.fit_predict(matrix)

    # Step 6: Outlier detection via average distances
    avg_distances = np.mean(dist_matrix, axis=1)
    outlier_indices = np.argsort(avg_distances)[-10:]

    # Step 7: Compute trustworthiness score
    trust_score = trustworthiness(dist_matrix, vectors_2d, n_neighbors=10)
    print(f"Trustworthiness of UMAP projection: {trust_score:.3f}")

    # Step 8: Optional: save plot
    if save_image_path:
        plt.figure(figsize=(10, 8))
        sns.scatterplot(x=vectors_2d[:, 0], y=vectors_2d[:, 1], hue=cluster_labels, palette="tab20", legend=False)
        sns.scatterplot(x=vectors_2d[outlier_indices, 0], y=vectors_2d[outlier_indices, 1], color='red', s=100, label='Outliers')
        plt.title("Qdrant Clusters (Trustworthiness: {:.3f})".format(trust_score))
        plt.savefig(save_image_path)
        plt.close()

    return vectors_2d, cluster_labels, outlier_indices, payloads, vectors

def get_nearest_neighbors(vector, top_k=5):
    client = QdrantClient(host="qdrant", port=6333)
    search_result = client.search(
        collection_name="ocorrencias_resumo_collection",
        query_vector=vector,
        limit=top_k,
        with_payload=True
    )
    neighbors = []
    for point in search_result:
        neighbors.append({
            'id': point.id,
            'score': point.score,
            'payload': point.payload,
            'vector': point.vector
        })
    return neighbors