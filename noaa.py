import pandas as pd
import sqlite3
import requests
from io import BytesIO
from tqdm import tqdm
import tarfile

def create_table_from_df(df, conn, table_name):
    columns = ', '.join([f"{col} TEXT" for col in df.columns])
    create_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns});"
    conn.execute(create_query)

# Define the URL pattern and years
base_url = "https://www.ncei.noaa.gov/data/global-hourly/archive/csv/"
years = range(2019, 2024)
db_file = 'noaa_data.db'

with sqlite3.connect(db_file) as conn:
    for year in years:
        file_url = f"{base_url}{year}.tar.gz"
        print(f"Processing data for year {year}...")

        try:
            response = requests.get(file_url, stream=True)
            response.raise_for_status()
            total_size_in_bytes = int(response.headers.get('content-length', 0))
            block_size = 1024

            file_stream = BytesIO()
            with tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True, desc=f"Downloading {year}", leave=False) as progress_bar:
                for data in response.iter_content(block_size):
                    progress_bar.update(len(data))
                    file_stream.write(data)

            file_stream.seek(0)
            with tarfile.open(fileobj=file_stream, mode="r:gz") as tar:
                for member in tqdm(tar.getmembers(), desc="Extracting files", leave=False):
                    if member.isfile() and member.name.endswith('.csv'):
                        csv_file = tar.extractfile(member)
                        df = pd.read_csv(csv_file, low_memory=False)
                        create_table_from_df(df, conn, 'noaa_data')
                        for chunk in tqdm(pd.read_csv(csv_file, chunksize=10**5), desc="Processing CSV", leave=False):
                            chunk.to_sql('noaa_data', conn, if_exists='append', index=False)
        except requests.RequestException as e:
            print(f"Error downloading data for year {year}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while processing data for year {year}: {e}")

print("Data import complete.")
