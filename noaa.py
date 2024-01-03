
from time import time
import datetime

import aiohttp
import asyncio
import pandas as pd
import sqlite3
from io import StringIO

def read_station_ids_by_year(file_path):
    station_ids_by_year = {}
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split(":")
            if len(parts) == 2:
                year, station_ids = parts
                station_ids_by_year[int(year)] = [s.strip() for s in station_ids.split(",")]
    return station_ids_by_year

def check_data_exists(conn, table_name, year, station_id):
    query = f"SELECT COUNT(*) FROM {table_name} WHERE year = ? AND station_id = ?"
    cur = conn.cursor()
    cur.execute(query, (year, station_id))
    return cur.fetchone()[0] > 0

async def download_station_data(session, year, station_id, chunksize=10000):
    url = f"https://www.ncei.noaa.gov/data/global-hourly/access/{year}/{station_id}.csv"
    try:
        async with session.get(url) as response:
            if response.status == 200:
                text = await response.text()
                return text, year, station_id
            else:
                print(f"Error: Unable to download data for station {station_id} in year {year}. HTTP status: {response.status}")
                return None, year, station_id
    except Exception as e:
        print(f"Error downloading data for station {station_id} in year {year}: {e}")
        return None, year, station_id

async def process_station_group(conn, year, station_ids, table_name, chunksize=10000):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for station_id in station_ids:
            if not check_data_exists(conn, table_name, year, station_id):
                task = download_station_data(session, year, station_id, chunksize)
                tasks.append(task)
            else:
                print(f"Data for station {station_id} in year {year} already exists. Skipping.")
        return await asyncio.gather(*tasks)

def initialize_year_table(conn, base_table_name, year):
    table_name = f"{base_table_name}_{year}"
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY,
            year INTEGER,
            station_id TEXT
        )
    """)
    conn.commit()
    return table_name

def update_table_schema(conn, table_name, df):
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table_name})")
    existing_columns = {col[1] for col in cur.fetchall()}
    for col in df.columns:
        if col not in existing_columns:
            col_type = "TEXT"  # Default to TEXT, adjust based on your needs
            cur.execute(f"ALTER TABLE {table_name} ADD COLUMN {col} {col_type}")
    conn.commit()

def insert_into_database(conn, table_name, data):
    if data is not None:
        update_table_schema(conn, table_name, data)
        data.to_sql(table_name, conn, if_exists='append', index=False)

def process_downloaded_data(conn, table_name, text, year, station_id, chunksize=10000):
    for chunk in pd.read_csv(StringIO(text), chunksize=chunksize):
        chunk['year'] = year
        chunk['station_id'] = station_id
        insert_into_database(conn, table_name, chunk)

def process_all_stations(station_ids_by_year, db_name="noaa_data.db", base_table_name="noaa_hourly_data", batch_size=50):
    with sqlite3.connect(db_name) as conn:
        for year, station_ids in station_ids_by_year.items():
            table_name = initialize_year_table(conn, base_table_name, year)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            results = loop.run_until_complete(process_station_group(conn, year, station_ids, table_name))
            loop.close()
            for text, year, station_id in results:
                if text is not None:
                    process_downloaded_data(conn, table_name, text, year, station_id)

if __name__ == "__main__":
    t0 = time()
    station_ids_by_year = read_station_ids_by_year("stations.txt")
    process_all_stations(station_ids_by_year)
    t1 = time()
    print(str(datetime.timedelta(seconds=round(t1-t0))))