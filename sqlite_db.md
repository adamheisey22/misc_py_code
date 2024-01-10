# Working with CSV Files and SQLite in Python

This guide provides two examples of how to work with CSV files and SQLite databases in Python. The first example demonstrates how to read multiple CSV files from a folder, concatenate them, and write the combined data to a SQLite database. The second example shows how to handle a single CSV file.

## Example 1: Multiple CSV Files

If you have multiple CSV files in a single folder and you want to combine them into a single SQLite database, you can use the following function.

### Function: `csv_to_sqlite`

```python
import pandas as pd
import sqlite3
import glob
import os

def csv_to_sqlite(folder_path, database_file):
    # Create a SQLite connection
    conn = sqlite3.connect(database_file)
    
    # Build the file path pattern
    pattern = os.path.join(folder_path, '*.csv')

    # Find all CSV files in the folder
    csv_files = glob.glob(pattern)

    # Read and concatenate all found CSV files
    concatenated_df = pd.concat([pd.read_csv(f) for f in csv_files], ignore_index=True)

    # Write the DataFrame to SQLite database
    concatenated_df.to_sql('data', conn, if_exists='replace', index=False)

    # Close the SQLite connection
    conn.close()

# Example usage
folder_path = 'path_to_your_folder'
database_file = 'output_database.db'
csv_to_sqlite(folder_path, database_file)
```

#### Explanation

- The function `csv_to_sqlite` takes two arguments: the path to the folder containing the CSV files (`folder_path`) and the path to the output SQLite database file (`database_file`).
- It uses the `glob` module to find all CSV files in the specified folder.
- These files are read and concatenated into a single pandas DataFrame.
- Finally, the DataFrame is written to a SQLite database, with the table name 'data'. If the table already exists, it will be replaced.

## Example 2: Single CSV File

When dealing with a single CSV file that you want to write to a SQLite database, you can use a more straightforward function.

### Function: `csv_to_sqlite_single`

```python
import pandas as pd
import sqlite3

def csv_to_sqlite_single(csv_file, database_file):
    # Create a SQLite connection
    conn = sqlite3.connect(database_file)
    
    # Read the CSV file
    df = pd.read_csv(csv_file)

    # Write the DataFrame to SQLite database
    df.to_sql('data', conn, if_exists='replace', index=False)

    # Close the SQLite connection
    conn.close()

# Example usage
csv_file = 'your_single_csv_file.csv'
database_file = 'output_database.db'
csv_to_sqlite_single(csv_file, database_file)
```

#### Explanation

- The function `csv_to_sqlite_single` takes the path to a single CSV file (`csv_file`) and the path to the output SQLite database file (`database_file`).
- It reads the CSV file into a pandas DataFrame.
- The DataFrame is then written to the SQLite database in the 'data' table. As before, any existing table with the same name will be replaced.
- The SQLite connection is closed after completing the operation.

### Prerequisites

To use these functions, ensure you have `pandas` installed in your Python environment (`pip install pandas`). SQLite functionality is provided by the `sqlite3` module, which is part of Python's standard library.

### Use Cases

These functions are useful for data manipulation tasks where you need to aggregate CSV data and store it in a database format for further analysis or processing.