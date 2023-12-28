import requests
import pandas as pd
import sqlite3
from io import StringIO
from concurrent.futures import ThreadPoolExecutor

def download_weather_data(station_id, year):
    base_url = "https://www.ncei.noaa.gov/data/global-hourly/access/"
    url = f"{base_url}{year}/{station_id}-{year}.csv"

    try:
        response = requests.get(url)
        response.raise_for_status()
        return pd.read_csv(StringIO(response.text))
    except requests.exceptions.RequestException as e:
        print(f"Failed to download data for station {station_id} and year {year}: {e}")
        return None

def download_and_process(station_id, year):
    weather_data = download_weather_data(station_id, year)
    if weather_data is not None:
        weather_data["station_id"] = station_id
    return weather_data, station_id

def concatenate_and_write_to_sqlite(stations, year, sqlite_file):
    conn = sqlite3.connect(sqlite_file)
    failed_stations = []

    # Download and process data in parallel
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(lambda s: download_and_process(s, year), stations))

    # Filter out failed downloads
    successful_results = [result[0] for result in results if result[0] is not None]
    failed_stations = [result[1] for result in results if result[0] is None]

    if successful_results:
        # Assuming that the table name is 'weather_data' and the structure is consistent
        # Adjust the table name and structure based on the actual data structure
        concatenated_data = pd.concat(successful_results, ignore_index=True)
        concatenated_data.to_sql("weather_data", conn, if_exists="append", index=False)

    conn.close()

    return failed_stations

# Example usage
stations = [123, 456, 789]  # Replace with your actual station IDs
year = 2019
sqlite_file = "weather_data.db"

failed_stations = concatenate_and_write_to_sqlite(stations, year, sqlite_file)

# Display the list of failed stations
if failed_stations:
    print("Stations failed to download:", failed_stations)
else:
    print("All stations downloaded successfully.")
