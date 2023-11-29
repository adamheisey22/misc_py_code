import requests
import pandas as pd

def fetch_eia_data(api_key, start_date, end_date, length=5000):
    url = 'https://api.eia.gov/v2/electricity/rto/region-sub-ba-data/data/'
    
    # Define the API parameters
    params = {
        'api_key': api_key,
        'frequency': 'hourly',
        'data[0]': 'value',
        'start': start_date,
        'end': end_date,
        'sort[0][column]': 'period',
        'sort[0][direction]': 'desc',
        'offset': 0,
        'length': length,
    }

    # Make the API request
    response = requests.get(url, params=params)
    data = response.json()

    # Extract the relevant data from the response
    series_data = data['series'][0]['data']

    # Convert the data to a Pandas DataFrame
    df = pd.DataFrame(series_data)

    return df

# Example usage:
api_key = 'YOUR_EIA_API_KEY'
start_date = '2023-01-01T00:00:00'
end_date = '2023-01-02T00:00:00'
length = 5000

eia_dataframe = fetch_eia_data(api_key, start_date, end_date, length)

# Display the resulting DataFrame
print(eia_dataframe)
