from dask.distributed import Client
import time

def slow_increment(x):
    time.sleep(15)  # simulate a long computation
    return x + 1

if __name__ == "__main__":
    client = Client("tcp://daskscheduler:8786")
    print("Connected to Dask cluster")

    futures = [client.submit(slow_increment, i) for i in range(10)]
    results = client.gather(futures)

    print(f"Results: {results}")
