FROM python:3.10-slim

WORKDIR /appVectorApi

COPY ./appVectorApi/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./appVectorApi .

CMD ["dask", "scheduler"]
