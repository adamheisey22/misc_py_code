# NOAA Hourly Data Download and Database Ingestion Script

## Overview

This script is designed to efficiently download and process hourly weather data from the National Oceanic and Atmospheric Administration (NOAA) for multiple stations across different years. The data is then stored in a SQLite database, with a separate table for each year to facilitate easy data management and retrieval.

## Features

- **Asynchronous Data Download**: Leverages Python's `asyncio` and `aiohttp` libraries for fast, asynchronous downloading of data from NOAA's website.
- **Chunked Data Processing**: Processes large CSV files in chunks to minimize memory usage.
- **Database Storage**: Stores data in a SQLite database, creating a new table for each year.
- **Dynamic Schema Adjustment**: Dynamically adjusts the database schema based on the columns present in the downloaded data.
- **Data Existence Check**: Before downloading, checks if the data for a particular station and year already exists in the database to avoid redundant downloads.

## Prerequisites

- Python 3.x
- `aiohttp` library (`pip install aiohttp`)
- `pandas` library (`pip install pandas`)
- SQLite

## Input Format

The script expects a text file named `stations.txt` containing station IDs for each year in the following format:

```
year: station_id1, station_id2, ...
year: station_id3, station_id4, ...
...
```

For example:

```
2019: 12345, 67890
2020: 23456, 78901
```

## Usage

1. Prepare the `stations.txt` file with the desired station IDs and years.
2. Run the script in a Python environment where the prerequisites are installed.

The script will do the following:

- Read the list of station IDs and corresponding years from `stations.txt`.
- For each year, it will check and create a new table in the SQLite database (`noaa_data.db`) if it does not already exist.
- It will download data for each station asynchronously, checking if data for that station and year already exists in the database.
- Downloaded data is processed in chunks and inserted into the respective year's table in the database.
- The database schema is dynamically updated based on the columns present in each chunk of the downloaded data.

## Error Handling

The script includes basic error handling, such as:

- Handling failed HTTP requests or network issues during data download.
- Skipping data download if the data for a specific station and year already exists in the database.
- Logging errors to the console for troubleshooting.

## Customization

Users can customize the script as follows:

- Modify the `stations.txt` file to include the specific station IDs and years of interest.
- Adjust the `batch_size` parameter in the `process_all_stations` function to balance network usage and performance.
- Change the database name and table naming convention as needed.

## Limitations

- The script is specifically tailored for NOAA's hourly data format and might not work with other data formats without modifications.
- It is designed to work with SQLite; using another database system would require adjustments to the database interaction code.
- The script assumes that the CSV files from NOAA are well-formed and consistent in format across different years and stations.