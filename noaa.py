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

            # Get the existing columns in the database
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info(weather_data);")
            existing_columns = [column_info[1] for column_info in cursor.fetchall()]

            # Identify new columns
            new_columns = list(set(data.columns) - set(existing_columns))

            # If there are new columns, add them to the SQLite table
            if new_columns:
                for new_column in new_columns:
                    cursor.execute(f"ALTER TABLE weather_data ADD COLUMN {new_column} TEXT;")
                conn.commit()

            # Append the data to the SQLite database
            data.to_sql('weather_data', conn, if_exists='append', index=False)
            print(f'Downloaded and added data for station {station_id}')
        else:
            print(f'Data file not found for station {station_id}')

    # Close the database connection
    conn.close()

# Example usage:
station_ids = [1, 2, 3]  # Replace with your actual station IDs
download_and_concatenate_weather_data(station_ids)
