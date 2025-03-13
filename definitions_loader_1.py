import os
import pandas as pd
import numpy as np

# Define input folders and corresponding schemas
FOLDERS = {
    "electricity": "elec_definitions.py",
    "hydrogen": "hydro_definitions.py",
    "integrator": "integ_definitions.py",
    "residential": "res_definitions.py",
}

# Function to infer SQLAlchemy column types based on Pandas dtypes
def infer_sqlalchemy_type(series):
    if np.issubdtype(series.dtype, np.integer):
        return "Integer"
    elif np.issubdtype(series.dtype, np.floating):
        return "Float"
    elif np.issubdtype(series.dtype, np.bool_):
        return "Boolean"
    else:
        return "String"  # Default for text/mixed types

# Iterate over each schema folder
for schema, output_file in FOLDERS.items():
    folder_path = schema  # Folder name matches schema
    definitions = f'''"""
Auto-generated SQLAlchemy ORM definitions for the {schema} schema.
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
Base = declarative_base(metadata=MetaData(schema="{schema}"))

'''

    # Process CSV files in the current folder
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            if filename.endswith(".csv"):
                table_name = filename.replace(".csv", "").lower()
                file_path = os.path.join(folder_path, filename)

                # Load CSV into DataFrame
                df = pd.read_csv(file_path)

                # Start defining class
                class_def = f"\nclass {table_name.capitalize()}(Base):\n"
                class_def += f'    __tablename__ = "{table_name}"\n'
                class_def += f'    __table_args__ = {{"schema": "{schema}"}}\n\n'
                class_def += '    id = Column(Integer, primary_key=True, autoincrement=True)\n'

                # Define columns dynamically
                for col in df.columns:
                    col_type = infer_sqlalchemy_type(df[col])
                    class_def += f'    {col} = Column({col_type})\n'

                # Append class definition
                definitions += class_def

        # Write the ORM definition file
        with open(output_file, "w") as f:
            f.write(definitions)

        print(f"Generated {output_file} for schema '{schema}'.")

print("All ORM definitions generated.")
