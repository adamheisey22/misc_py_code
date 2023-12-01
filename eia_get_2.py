import requests
import pandas as pd
import fastparquet as fp
from datetime import datetime, timedelta

def fetch_eia_data(api_url, offset, length):
    params = {
        'offset': offset,
        'length': length
    }
    response = requests.get(api_url, params=params)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error: {response.status_code}")
        return None

def convert_to_dataframe(api_data):
    try:
        series_data = api_data['response']['data']
        df = pd.DataFrame(series_data)
        
        # Convert 'subba' column to string
        df['subba'] = df['subba'].astype(str)
        
        df['period'] = pd.to_datetime(df['period'])
        return df
    except KeyError as e:
        print(f"KeyError: {e}")
        return None

def save_to_parquet(df, file_path):
    # Check if the file exists
    try:
        existing_df = pd.read_parquet(file_path)
        combined_df = pd.concat([existing_df, df], ignore_index=True)
    except FileNotFoundError:
        combined_df = df

    fp.write(file_path, combined_df, compression='SNAPPY', row_group_offsets=500000)

if __name__ == "__main__":
    api_url = "https://api.eia.gov/v2/electricity/rto/region-sub-ba-data/data/?frequency=hourly&data[0]=value&sort[0][column]=period&sort[0][direction]=desc"
    chunk_size = 5000
    current_offset = 0

    while True:
        print(f"Fetching data for offset {current_offset} to {current_offset + chunk_size}")
        
        api_data = fetch_eia_data(api_url, offset=current_offset, length=chunk_size)
        
        if api_data is not None:
            df = convert_to_dataframe(api_data)
            
            if df is not None and not df.empty:
                print(df.head())
                
                # Save data to Parquet file (append mode)
                save_to_parquet(df, "output_data.parquet")
                
                # Update offset for the next iteration
                current_offset += chunk_size
            else:
                print("No more data available.")
                break
        else:
            print("Failed to fetch data.")
            break
