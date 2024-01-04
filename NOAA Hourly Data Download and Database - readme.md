# NOAA Hourly Data Download and Database Ingestion Script

## Overview

This Python script is designed for efficiently downloading NOAA (National Oceanic and Atmospheric Administration) hourly weather data for multiple stations across various years. It stores the downloaded data in a SQLite database, creating distinct tables for each year, which allows for effective data organization and retrieval.

## Features

- **Asynchronous Downloading**: Uses Python's `asyncio` and `aiohttp` libraries for simultaneous and non-blocking data downloads.
- **Chunked Data Processing**: Handles large CSV files in chunks to optimize memory usage.
- **Database Storage with SQLite**: Utilizes SQLite for data storage, creating separate tables for each year's data.
- **Dynamic Schema Management**: Dynamically updates the database schema based on the content of the downloaded CSV files.
- **Data Existence Check**: Prioritizes efficiency by checking if the data for a particular station-year combination already exists in the database before downloading.
- **Rate Limiting**: Implements a delay between download requests to prevent server throttling.
- **Database Indexing**: Enhances query performance by indexing tables on frequently queried columns (`year` and `station_id`).

## Prerequisites

- Python 3.x
- `aiohttp` library for asynchronous HTTP requests (`pip install aiohttp`)
- `pandas` library for data handling (`pip install pandas`)
- SQLite for database operations

## Input File Format

The script requires an input file named `stations.txt`, formatted as follows:

```
year: station_id1, station_id2, ...
year: station_id3, station_id4, ...
...
```

Each line should list a year followed by station IDs separated by commas.

## Script Workflow

1. **Initialization**: Reads station IDs and corresponding years from `stations.txt`.

2. **Database Table Creation**: For each year, checks if a corresponding table exists in the SQLite database; if not, it creates one with initial columns (`id`, `year`, `station_id`) and adds necessary indexes.

3. **Data Download and Processing**:
    - Checks if data for a given station and year already exists in the database.
    - If not, asynchronously downloads CSV data from NOAA's website.
    - Incorporates a delay between requests to mitigate potential server throttling.
    - Processes downloaded CSV files in chunks, dynamically adding any new columns found in the CSV to the database table.
    - Inserts data into the respective year's table.

4. **Error Handling**: Captures and logs errors encountered during the download or processing phases.

## Customization

Users can customize the script as follows:

- Modify `stations.txt` to include specific station IDs and years.
- Adjust the `batch_size` parameter in `process_all_stations` to balance network load and performance.
- The delay between requests can be changed by modifying the `delay` parameter in `process_station_group`.

## Limitations

- Designed specifically for NOAA's hourly data and may need adjustments for other datasets.
- Best suited for SQLite; using a different database system would require modifications.
- Assumes consistent CSV format across different years and stations.

This script efficiently handles the download and storage of extensive NOAA weather data, making it a useful tool for researchers and analysts working with environmental data.