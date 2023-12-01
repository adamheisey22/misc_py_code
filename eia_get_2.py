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
    fp.write(file_path, df, compression='SNAPPY', row_group_offsets=500000)

if __name__ == "__main__":
    api_url = "https://api.eia.gov/v2/electricity/rto/region-sub-ba-data/data/?api_key=WOLU5avflX0tFNVkVuShl4z2Pj3vyee7Z5n40O46&frequency=hourly&data[0]=value&sort[0][column]=period&sort[0][direction]=desc"

    start_date = datetime(2018, 1, 1, 0)
    end_date = datetime(2023, 1, 1, 0)
    chunk_size = 5000
    current_date = start_date
    parquet_file_path = "output_data.parquet"

    while current_date < end_date:
        print(f"Fetching data for {current_date} to {current_date + timedelta(hours=chunk_size)}")

        api_data = fetch_eia_data(api_url, offset=0, length=chunk_size)

        if api_data is not None:
            df = convert_to_dataframe(api_data)

            if df is not None:
                print(df.head())

                # Save data to Parquet file (append mode)
                save_to_parquet(df, parquet_file_path)

                # Update current date for the next iteration
                current_date += timedelta(hours=chunk_size)
            else:
                print("Failed to convert data to DataFrame.")
                break
        else:
            print("Failed to fetch data.")
            break
