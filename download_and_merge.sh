#!/bin/bash

# Specify the years and the output SQLite database file
years=(2022 2023)
output_db="eia930_balance.db"

# Initialize an array to store CSV file paths
csv_files=()

# Loop through each year and download CSV files
for year in "${years[@]}"; do
    url_jan_jun="https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/EIA930_BALANCE_${year}_Jan_Jun.csv"
    url_jul_dec="https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/EIA930_BALANCE_${year}_Jul_Dec.csv"

    # Download CSV files and store their paths
    csv_files+=("EIA930_BALANCE_${year}_Jan_Jun.csv" "EIA930_BALANCE_${year}_Jul_Dec.csv")
    wget "$url_jan_jun"
    wget "$url_jul_dec"
done

# Concatenate CSV files
cat "${csv_files[@]}" > concatenated_data.csv

# Convert CSV to SQLite
csvsql --db sqlite:///"$output_db" --insert concatenated_data.csv

# Clean up: remove downloaded CSV files and the concatenated file
rm "${csv_files[@]}" concatenated_data.csv

echo "Data for years ${years[*]} has been downloaded and written to $output_db."
