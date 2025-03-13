import os
import pandas as pd
import numpy as np

# Path to the folder containing CSV files
FOLDER_PATH = "cem_inputs"

# Function to infer SQLAlchemy column types based on Pandas dtypes
def infer_sqlalchemy_type(series):
    if np.issubdtype(series.dtype, np.integer):
        return "Integer"
    elif np.issubdtype(series.dtype, np.floating):
        return "Float"
    elif np.issubdtype(series.dtype, np.bool_):
        return "Boolean"
    else:
        return "String"  # Default to String for text/mixed types

# Template for the definitions file
definitions = '''"""
Auto-generated SQLAlchemy ORM definitions for the electricity schema.

This file defines ORM classes for tables based on CSV files.
"""

from sqlalchemy import Column, Integer, Float, String, Boolean, create_engine, MetaData
from sqlalchemy.orm import declarative_base, sessionmaker

# Database connection settings
DB_URL = "postgresql+psycopg2://your_username:your_password@localhost:5432/your_database"

# Create database engine
engine = create_engine(DB_URL)

# Create session
Session = sessionmaker(bind=engine)
session = Session()

# Base class for ORM models
Base = declarative_base(metadata=MetaData(schema="electricity"))

'''

# Iterate over CSV files to generate ORM classes
for filename in os.listdir(FOLDER_PATH):
    if filename.endswith(".csv"):
        table_name = filename.replace(".csv", "").lower()
        file_path = os.path.join(FOLDER_PATH, filename)

        # Load CSV into DataFrame
        df = pd.read_csv(file_path)

        # Start defining class
        class_def = f"\nclass {table_name.capitalize()}(Base):\n"
        class_def += f'    __tablename__ = "{table_name}"\n'
        class_def += '    __table_args__ = {"schema": "electricity"}\n\n'
        class_def += '    id = Column(Integer, primary_key=True, autoincrement=True)\n'

        # Define columns
        for col in df.columns:
            col_type = infer_sqlalchemy_type(df[col])
            class_def += f'    {col} = Column({col_type})\n'

        # Append class definition to the script
        definitions += class_def

# Write to `elec_definitions.py`
with open("elec_definitions.py", "w") as f:
    f.write(definitions)

print("Generated elec_definitions.py with ORM class definitions.")
