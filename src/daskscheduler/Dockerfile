FROM python:3.10-slim

# WORKDIR /appVectorApi
WORKDIR /daskscheduler

# COPY ./appVectorApi/requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

# COPY ./appVectorApi .

# COPY ./

CMD ["dask", "scheduler"]
