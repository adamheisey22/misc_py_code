import requests
import tarfile
import sqlite3
import pandas as pd
from io import BytesIO
from tqdm import tqdm

# Define the URL pattern and years
base_url = "https://www.ncei.noaa.gov/data/global-hourly/archive/csv/"
years = range(2019, 2024)

# SQLite database setup
db_file = 'noaa_data.db'
conn = sqlite3.connect(db_file)

# Function to process and load a single CSV file into the database
def process_csv(file_stream):
    chunksize = 10 ** 5
    for chunk in tqdm(pd.read_csv(file_stream, chunksize=chunksize, low_memory=False), desc="Processing CSV", leave=False):
        chunk.to_sql('noaa_data', conn, if_exists='append', index=False)

# Download, stream, and process each year's data
for year in years:
    file_url = f"{base_url}{year}.tar.gz"
    print(f"Processing data for year {year}...")

    try:
        with requests.get(file_url, stream=True) as response:
            response.raise_for_status()  # Check if the request was successful
            total_size_in_bytes = int(response.headers.get('content-length', 0))
            block_size = 1024  # 1 Kibibyte

            file_stream = BytesIO()
            with tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True, desc=f"Downloading {year}") as progress_bar:
                for data in response.iter_content(block_size):
                    progress_bar.update(len(data))
                    file_stream.write(data)

            file_stream.seek(0)
            with tarfile.open(fileobj=file_stream, mode="r:gz") as tar:
                for member in tar.getmembers():
                    if member.isfile() and member.name.endswith('.csv'):
                        csv_file = tar.extractfile(member)
                        process_csv(csv_file)
    except requests.RequestException as e:
        print(f"Error downloading data for year {year}: {e}")

# Close database connection
conn.close()
print("Data import complete.")
