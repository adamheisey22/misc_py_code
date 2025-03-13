import os
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, Float, String, Boolean, MetaData
from sqlalchemy.orm import declarative_base, sessionmaker
import numpy as np

# Database connection settings
DB_URL = "postgresql+psycopg2://your_username:your_password@localhost:5432/your_database"
FOLDER_PATH = "cem_inputs"

# Create database engine and session
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Ensure the schema exists
with engine.connect() as conn:
    conn.execute("CREATE SCHEMA IF NOT EXISTS electricity;")
    conn.commit()

# Base class for ORM models
Base = declarative_base(metadata=MetaData(schema="electricity"))

# Function to infer SQLAlchemy column types based on Pandas dtypes
def infer_sqlalchemy_type(series):
    if np.issubdtype(series.dtype, np.integer):
        return Integer
    elif np.issubdtype(series.dtype, np.floating):
        return Float
    elif np.issubdtype(series.dtype, np.bool_):
        return Boolean
    else:
        return String  # Default to String for object or unknown types

# Function to dynamically create ORM table classes
def create_table_class(table_name, df):
    attrs = {"__tablename__": table_name, "__table_args__": {"schema": "electricity"}}
    attrs["id"] = Column(Integer, primary_key=True, autoincrement=True)  # Auto ID column

    for col in df.columns:
        col_type = infer_sqlalchemy_type(df[col])
        attrs[col] = Column(col_type)

    return type(table_name, (Base,), attrs)

# Iterate over CSV files in the folder
for filename in os.listdir(FOLDER_PATH):
    if filename.endswith(".csv"):
        table_name = filename.replace(".csv", "").lower()
        file_path = os.path.join(FOLDER_PATH, filename)

        # Load CSV into DataFrame
        df = pd.read_csv(file_path)

        # Dynamically create table class
        TableClass = create_table_class(table_name, df)

        # Create table in database
        Base.metadata.create_all(engine)

        # Insert data into table
        df.to_sql(table_name, engine, schema="electricity", if_exists="append", index=False)

        print(f"Table '{table_name}' created with inferred column types and data loaded.")

# Close session
session.close()
