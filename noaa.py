import os
import requests
import pandas as pd
import sqlite3

def download_and_concatenate_weather_data(stations, output_database='weather_data.db'):
    base_url = 'https://www.ncei.noaa.gov/data/global-hourly/access/2019/'

    # Create SQLite database connection
    conn = sqlite3.connect(output_database)

    for station_id in stations:
        data_file_name = f'{station_id}_2019.csv'
        data_file_url = f'{base_url}{data_file_name}'

        # Check if the data file exists
        response = requests.head(data_file_url)
        if response.status_code == 200:
            # Download the data
            data = pd.read_csv(data_file_url)

            # Add station ID as a column
            data['station_id'] = station_id

            # Concatenate the data to the SQLite database
            data.to_sql('weather_data', conn, if_exists='append', index=False)

            print(f'Downloaded and added data for station {station_id}')
        else:
            print(f'Data file not found for station {station_id}')

    # Close the database connection
    conn.close()

# Example usage:
station_ids = [1, 2, 3]  # Replace with your actual station IDs
download_and_concatenate_weather_data(station_ids)
