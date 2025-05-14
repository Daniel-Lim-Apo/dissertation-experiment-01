FROM python:3.10

WORKDIR /appVectorVisualizer

ENV TZ=America/Sao_Paulo

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
