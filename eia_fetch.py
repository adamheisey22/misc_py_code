import requests
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from datetime import datetime, timedelta

def fetch_eia_data(api_key, start_date, end_date, rows_per_iteration=5000, output_file='eia_data.parquet'):
    base_url = 'http://api.eia.gov/series/'
    
    current_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')

    # Create an empty DataFrame to store the fetched data
    all_data = pd.DataFrame()

    while current_date <= end_date:
        formatted_date = current_date.strftime('%Y%m%d')

        # Define the API parameters
        payload = {
            'api_key': api_key,
            'series_id': 'YOUR_SERIES_ID',  # Replace with the actual EIA series ID
            'start': formatted_date,
            'end': formatted_date,
        }

        # Make the API request
        response = requests.get(base_url, params=payload)
        data = response.json()['series'][0]['data']

        # Convert the data to a DataFrame
        df = pd.DataFrame(data, columns=['date', 'value'])
        df['date'] = pd.to_datetime(df['date'])
        
        # Append the data to the overall DataFrame
        all_data = pd.concat([all_data, df], ignore_index=True)

        # Move to the next date
        current_date += timedelta(days=1)

        # Check if we have accumulated enough rows
        if len(all_data) >= rows_per_iteration:
            # Write the current batch to the Parquet file
            write_parquet(all_data, output_file)
            
            # Reset the DataFrame for the next batch
            all_data = pd.DataFrame()

    # Write any remaining data to the Parquet file
    write_parquet(all_data, output_file)


def write_parquet(data, output_file):
    # Convert the DataFrame to a PyArrow Table
    table = pa.Table.from_pandas(data)

    # Write the table to a Parquet file
    with pq.ParquetWriter(output_file, table.schema) as writer:
        writer.write_table(table)


# Example usage:
api_key = 'YOUR_EIA_API_KEY'
start_date = '2023-01-01'
end_date = '2023-01-10'
fetch_eia_data(api_key, start_date, end_date)
