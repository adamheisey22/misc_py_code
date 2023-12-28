import os
import requests
import tarfile
import pandas as pd
import concurrent.futures
import dask.dataframe as dd
from io import BytesIO

# Function to download and extract data for a specific year
def download_and_extract(year):
    url = f'https://www.ncei.noaa.gov/data/global-hourly/archive/csv/{year}.tar.gz'
    response = requests.get(url)

    if response.status_code == 200:
        # Extract data from the tar.gz file
        with tarfile.open(fileobj=BytesIO(response.content), mode="r:gz") as tar:
            tar.extractall(path=f"./{year}")
    else:
        print(f"Failed to download data for {year}")

# Download and extract data for 2019 and 2020 concurrently
with concurrent.futures.ThreadPoolExecutor() as executor:
    years = [2019, 2020]
    futures = {executor.submit(download_and_extract, year): year for year in years}

    for future in concurrent.futures.as_completed(futures):
        year = futures[future]
        try:
            future.result()
            print(f"Download and extraction for {year} completed.")
        except Exception as e:
            print(f"Error downloading or extracting data for {year}: {e}")

# Create Dask DataFrames for each year and concatenate them
df_list = []
for year in [2019, 2020]:
    folder_path = f"./{year}"
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        ddf = dd.read_csv(file_path, assume_missing=True)
        df_list.append(ddf)

# Concatenate all Dask DataFrames into a single Dask DataFrame
final_ddf = dd.concat(df_list, axis=0)

# Compute the result to obtain a Pandas DataFrame
final_df = final_ddf.compute()

# Display information about the final DataFrame
print(final_df.info())
