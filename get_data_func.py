import pandas as pd
import sqlite3
import requests

def download_and_merge_csv(years, output_db):
    # Initialize an empty list to store DataFrames for each year
    all_data = []

    for year in years:
        # Define the URLs for the CSV files
        url_jul_dec = f'https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/EIA930_BALANCE_{year}_Jul_Dec.csv'
        url_jan_jun = f'https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/EIA930_BALANCE_{year}_Jan_Jun.csv'

        # Download CSV data from the URLs
        data_jul_dec = pd.read_csv(url_jul_dec)
        data_jan_jun = pd.read_csv(url_jan_jun)

        # Append DataFrames to the list
        all_data.append(data_jan_jun)
        all_data.append(data_jul_dec)

    # Concatenate all DataFrames in the list
    merged_data = pd.concat(all_data, ignore_index=True)

    # Write the concatenated data to an SQLite database
    conn = sqlite3.connect(output_db)
    merged_data.to_sql('eia930_balance', conn, index=False, if_exists='replace')
    conn.close()

    print(f'Data for years {", ".join(map(str, years))} has been downloaded and written to {output_db}.')

# Specify the years and the output SQLite database file
download_and_merge_csv([2022, 2023], 'eia930_balance.db')
