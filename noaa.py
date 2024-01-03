import datetime
from time import time
import requests
import pandas as pd
import sqlite3
import threading
from io import StringIO
from tqdm import tqdm

def read_station_ids(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip()]

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

def process_station_id(station_id, start_year=2019, end_year=2023, table_name="noaa_hourly_data"):
    with sqlite3.connect("noaa_data.db") as conn:
        for year in tqdm(range(start_year, end_year + 1), desc=f"Processing {station_id}"):
            download_and_process_data(year, station_id, conn, table_name)

def process_all_stations(station_ids, table_name="noaa_hourly_data"):
    with sqlite3.connect("noaa_data.db") as conn:
        conn.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY)")
    threads = []
    for station_id in station_ids:
        thread = threading.Thread(target=process_station_id, args=(station_id, 2019, 2023, table_name))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

t0 = time()

# Example usage
station_ids = read_station_ids("stations.txt")
process_all_stations(station_ids)

t1 = time()

print(str(datetime.timedelta(seconds=round(t1-t0))))
