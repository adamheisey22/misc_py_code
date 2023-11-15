import os
import pandas as pd
import h5py

def process_csv_files(input_folder, output_file):
    # Ensure the output file does not exist
    if os.path.exists(output_file):
        raise FileExistsError("Output file already exists. Please provide a different file name.")

    # List all CSV files in the input folder
    csv_files = [f for f in os.listdir(input_folder) if f.endswith('.csv')]

    # Create an HDF5 file
    with h5py.File(output_file, 'w') as hdf_file:
        # Loop through each CSV file
        for csv_file in csv_files[:20]:  # Keep only the first 20 files
            csv_path = os.path.join(input_folder, csv_file)

            # Read CSV file
            df = pd.read_csv(csv_path, usecols=range(20))  # Keep only the first 20 columns

            # Convert DataFrame to NumPy array
            data_array = df.to_numpy()

            # Create a dataset in the HDF5 file
            hdf_file.create_dataset(csv_file.replace('.csv', ''), data=data_array)

    print(f"Data from {len(csv_files[:20])} CSV files saved to {output_file}")

# Example usage
input_folder_path = '/path/to/csv/files'
output_hdf5_file = '/path/to/output/file.h5'
process_csv_files(input_folder_path, output_hdf5_file)





import os
import pandas as pd
import concurrent.futures
import fastparquet

def process_csv_file(csv_path):
    # Read CSV file
    df = pd.read_csv(csv_path, usecols=range(20))  # Keep only the first 20 columns
    return df

def process_csv_files(input_folder, output_file):
    # Ensure the output file does not exist
    if os.path.exists(output_file):
        raise FileExistsError("Output file already exists. Please provide a different file name.")

    # List all CSV files in the input folder
    csv_files = [f for f in os.listdir(input_folder) if f.endswith('.csv')][:20]  # Keep only the first 20 files

    # Create an empty DataFrame to concatenate results
    all_data = pd.DataFrame()

    # Use concurrent processing to read CSV files in parallel
    with concurrent.futures.ProcessPoolExecutor() as executor:
        # Process each CSV file concurrently
        dfs = executor.map(process_csv_file, [os.path.join(input_folder, csv_file) for csv_file in csv_files])

    # Concatenate the DataFrames
    all_data = pd.concat(dfs, ignore_index=True)

    # Write to Parquet file
    all_data.to_parquet(output_file, index=False)

    print(f"Data from {len(csv_files)} CSV files saved to {output_file}")

# Example usage
input_folder_path = '/path/to/csv/files'
output_parquet_file = '/path/to/output/file.parquet'
process_csv_files(input_folder_path, output_parquet_file)
