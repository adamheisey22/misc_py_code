import requests
import pandas as pd
import sqlite3
import threading
from io import StringIO
from tqdm import tqdm

def read_station_ids_by_year(file_path):
    station_ids_by_year = {}
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split(":")
            if len(parts) == 2:
                year, station_ids = parts
                station_ids_by_year[int(year)] = [s.strip() for s in station_ids.split(",")]
    return station_ids_by_year

def update_table_schema(conn, table_name, new_columns):
    existing_cols = pd.read_sql(f"PRAGMA table_info({table_name})", conn)['name']
    for col in new_columns:
        if col not in existing_cols.to_list():
            conn.execute(f"ALTER TABLE {table_name} ADD COLUMN [{col}]")

def download_and_process_data(year, station_id, conn, table_name, chunksize=10000):
    url = f"https://www.ncei.noaa.gov/data/global-hourly/access/{year}/{station_id}.csv"
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        first_chunk = True
        for chunk in pd.read_csv(StringIO(response.text), chunksize=chunksize):
            if first_chunk:
                update_table_schema(conn, table_name, chunk.columns)
                first_chunk = False
            chunk.to_sql(name=table_name, con=conn, if_exists='append', index=False)

def process_station_id_for_year(year, station_ids, table_name="noaa_hourly_data"):
    with sqlite3.connect("noaa_data.db") as conn:
        for station_id in station_ids:
            tqdm_desc = f"Processing {station_id} for year {year}"
            for _ in tqdm(range(1), desc=tqdm_desc):
                download_and_process_data(year, station_id, conn, table_name)

def process_all_stations(station_ids_by_year, table_name="noaa_hourly_data"):
    with sqlite3.connect("noaa_data.db") as conn:
        conn.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY)")
    threads = []
    for year, station_ids in station_ids_by_year.items():
        thread = threading.Thread(target=process_station_id_for_year, args=(year, station_ids, table_name))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

# Example usage
station_ids_by_year = read_station_ids_by_year("stations.txt")
process_all_stations(station_ids_by_year)
