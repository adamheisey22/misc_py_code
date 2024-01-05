### Markdown Guide for SQL Processing Code

The provided code allows you to run SQL queries or execute SQL scripts using Python. It can process a `.sql` file or a custom SQL query in a Jupyter Notebook. Below are two examples demonstrating how to use this code.

#### Example 1: Using a .SQL File

In this example, we use a `.sql` file to run a query. This method is useful when you have complex queries stored in a file.

```python
from pathlib import Path
from time import time
import datetime
import pandas as pd
import requests
import sqlite3

# Assume the provided functions are already defined here

# Establish a database connection (example with SQLite)
conn = sqlite3.connect('your_database.db')

# Path to your .sql file
sql_file_path = "path/to/your_query.sql"

# Run the query from the .sql file
result_df = sql_run(conn, sql_file_path)

# Display the results
print(result_df)
```

In this example, you need to replace `'your_database.db'` with the path to your database and `path/to/your_query.sql` with the path to your `.sql` file.

#### Example 2: Using a Custom SQL Query in a Notebook

This example demonstrates how to run a custom SQL query directly in a Jupyter Notebook.

```python
from pathlib import Path
from time import time
import datetime
import pandas as pd
import requests
import sqlite3

# Assume the provided functions are already defined here

# Establish a database connection (example with SQLite)
conn = sqlite3.connect('your_database.db')

# Write your SQL query as a string
sql_query = """
SELECT *
FROM your_table
WHERE condition = 'value';
"""

# Run the query
result_df = sql_run(conn, sql_query)

# Display the results
print(result_df)
```

Replace `'your_database.db'` with your database path, `your_table` with your target table name, and the `condition = 'value'` with your specific query conditions.

These examples demonstrate how the provided functions can be integrated into Python scripts for database querying, either through an external `.sql` file or a direct SQL string in a Jupyter Notebook.