import requests
import pandas as pd

def fetch_eia_data(api_url):
    response = requests.get(api_url)

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
        df['period'] = pd.to_datetime(df['period'])
        return df
    except KeyError as e:
        print(f"KeyError: {e}")
        return None

if __name__ == "__main__":
    api_url = "https://api.eia.gov/v2/electricity/rto/region-sub-ba-data/data/?api_key=WOLU5avflX0tFNVkVuShl4z2Pj3vyee7Z5n40O46&frequency=hourly&data[0]=value&start=2023-01-01T00&end=2023-01-02T00&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000"

    api_data = fetch_eia_data(api_url)

    if api_data is not None:
        print(api_data)
        df = convert_to_dataframe(api_data)

        if df is not None:
            print(df.head())
        else:
            print("Failed to convert data to DataFrame.")
    else:
        print("Failed to fetch data.")