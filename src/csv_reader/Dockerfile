FROM bitnami/spark:latest

# Install Python and dependencies
USER root
RUN apt-get update && apt-get install -y python3 python3-pip && \
    pip3 install pandas && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY main.py .

CMD ["spark-submit", "--master", "spark://spark-master:7077", "main.py"]
