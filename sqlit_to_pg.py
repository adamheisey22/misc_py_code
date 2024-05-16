import pandas as pd
from sqlalchemy import create_engine

# Function to load data from SQLite
def load_data_from_sqlite(sqlite_db_path, table_name):
    sqlite_engine = create_engine(f'sqlite:///{sqlite_db_path}')
    df = pd.read_sql_table(table_name, sqlite_engine)
    return df

# Function to save data to PostgreSQL
def save_data_to_postgres(df, postgres_connection_string, table_name):
    postgres_engine = create_engine(postgres_connection_string)
    df.to_sql(table_name, postgres_engine, if_exists='replace', index=False)

# Function to migrate all tables
def migrate_all_tables(sqlite_db_path, postgres_connection_string):
    sqlite_engine = create_engine(f'sqlite:///{sqlite_db_path}')
    table_names = sqlite_engine.table_names()

    for table_name in table_names:
        df = load_data_from_sqlite(sqlite_db_path, table_name)
        save_data_to_postgres(df, postgres_connection_string, table_name)
        print(f"Table {table_name} migrated successfully.")

# Paths and connection strings
sqlite_db_path = 'path/to/your/sqlite.db'
postgres_connection_string = 'postgresql://username:password@localhost:5432/your_postgres_db'

# Migrate all tables
migrate_all_tables(sqlite_db_path, postgres_connection_string)
