import aiohttp
import asyncio
import pandas as pd
import sqlite3
from io import StringIO
import time

def read_station_ids_by_year(file_path):
    station_ids_by_year = {}
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split(":")
            if len(parts) == 2:
                year, station_ids = parts
                station_ids_by_year[int(year)] = [s.strip() for s in station_ids.split(",")]
    return station_ids_by_year

def get_existing_station_years(conn, table_name):
    query = f"SELECT year, station_id FROM {table_name}"
    cur = conn.cursor()
    cur.execute(query)
    return {(row[0], row[1]) for row in cur.fetchall()}

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

async def process_station_group(conn, year, station_ids, table_name, existing_data, chunksize=10000, delay=0.5):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for station_id in station_ids:
            if (year, station_id) not in existing_data:
                await asyncio.sleep(delay)  # Rate limiting
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
    conn.execute(f"CREATE INDEX IF NOT EXISTS idx_year ON {table_name}(year)")
    conn.execute(f"CREATE INDEX IF NOT EXISTS idx_station_id ON {table_name}(station_id)")
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
            existing_data = get_existing_station_years(conn, table_name)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            results = loop.run_until_complete(process_station_group(conn, year, station_ids, table_name, existing_data))
            loop.close()
            for text, year, station_id in results:
                if text is not None:
                    process_downloaded_data(conn, table_name, text, year, station_id)

if __name__ == "__main__":
    station_ids_by_year = read_station_ids_by_year("stations.txt")
    process_all_stations(station_ids_by_year)
