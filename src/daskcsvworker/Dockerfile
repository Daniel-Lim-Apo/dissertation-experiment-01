FROM python:3.10-slim

WORKDIR /app

ENV TZ=America/Sao_Paulo

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY reader.py .

CMD ["python", "reader.py"]
