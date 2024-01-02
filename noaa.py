import requests
import tarfile
import sqlite3
import pandas as pd
from io import BytesIO

# Define the URL pattern and years
base_url = "https://www.ncei.noaa.gov/data/global-hourly/archive/csv/"
years = range(2019, 2024)

# SQLite database setup
db_file = 'noaa_data.db'
conn = sqlite3.connect(db_file)

# Function to process and load a single CSV file into the database
def process_csv(file_stream):
    chunksize = 10 ** 5  # Adjusted for lower memory usage
    try:
        for chunk in pd.read_csv(file_stream, chunksize=chunksize, low_memory=False):
            chunk.to_sql('noaa_data', conn, if_exists='append', index=False)
    except pd.errors.EmptyDataError:
        print("Warning: Encountered an empty CSV file.")

# Download, stream, and process each year's data
for year in years:
    file_url = f"{base_url}{year}.tar.gz"
    print(f"Processing data for year {year}...")

    try:
        response = requests.get(file_url, stream=True)
        response.raise_for_status()  # Check if the request was successful

        file_stream = BytesIO(response.content)

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
