FROM python:3.10-slim

WORKDIR /appQdrantVisualizer

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

CMD ["python", "-m", "app.main"]
