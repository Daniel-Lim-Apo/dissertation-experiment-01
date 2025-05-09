from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from qdrant_client import QdrantClient
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import numpy as np
import plotly.express as px

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/")
def visualize_vectors(request: Request):
    # Connect to Qdrant
    client = QdrantClient(host="qdrant", port=6333)
    
    # Fetch points from the collection
    hits, _ = client.scroll(collection_name="text_vectors", limit=1000)

    # Filter valid vectors
    vectors = []
    for point in hits:
        if point.vector is not None and all(np.isfinite(point.vector)):
            vectors.append(point.vector)

    vectors = np.array(vectors)

    # Check if we have valid vectors
    if len(vectors) == 0:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "plot_html": "<h2>No valid vectors found in the 'text_vectors' collection.</h2>"
        })

    # Perform clustering
    kmeans = KMeans(n_clusters=5, random_state=42)
    labels = kmeans.fit_predict(vectors)

    # Reduce to 2D
    reduced = PCA(n_components=2).fit_transform(vectors)

    # Generate plot
    fig = px.scatter(x=reduced[:, 0], y=reduced[:, 1],
                     color=labels.astype(str),
                     title="Clustered Vectors from Qdrant (text_vectors)")

    plot_html = fig.to_html(full_html=False)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "plot_html": plot_html
    })
