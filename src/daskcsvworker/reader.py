import dask.dataframe as dd
from dask.distributed import Client
import os
import dask

# Optional: enable new query planner
dask.config.set({'dataframe.query-planning': True})

def main():
    client = Client("tcp://daskscheduler:8786")
    print("Connected to Dask scheduler.")

    csv_path = "/data/ocorrencias.csv"
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"File not found: {csv_path}")

    print(f"Reading CSV from {csv_path}")
    df = dd.read_csv(csv_path, sep=';', assume_missing=True)

    print("Columns:", df.columns)
    print("Partition count:", df.npartitions)

    output_dir = "/output/ocorrencias_parquet"
    os.makedirs(output_dir, exist_ok=True)  # 🔧 Ensure directory exists
    df.to_parquet(output_dir, engine="pyarrow", write_index=False)
    print(f"Data written to {output_dir} in Parquet format.")

if __name__ == "__main__":
    main()
