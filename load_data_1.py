import os
import pandas as pd
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import importlib

# Define schemas and corresponding definition modules
SCHEMA_DEFINITIONS = {
    "electricity": "elec_definitions",
    "hydrogen": "hydro_definitions",
    "integrator": "integ_definitions",
    "residential": "res_definitions",
}

# Iterate over schemas and load data
for schema, module_name in SCHEMA_DEFINITIONS.items():
    folder_path = schema  # Folder name matches schema

    # Import the corresponding ORM definition module dynamically
    module = importlib.import_module(module_name)
    Base = module.Base
    engine = module.engine
    Session = module.Session

    # Create a session
    session = Session()

    # Get table mappings from ORM definitions
    table_classes = {cls.__tablename__: cls for cls in Base.__subclasses__()}

    # Check if folder exists
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            if filename.endswith(".csv"):
                table_name = filename.replace(".csv", "").lower()
                file_path = os.path.join(folder_path, filename)

                # Check if the corresponding table class exists
                if table_name in table_classes:
                    TableClass = table_classes[table_name]
                    df = pd.read_csv(file_path)

                    # Convert dataframe to a list of dictionaries for ORM bulk insert
                    records = df.to_dict(orient="records")

                    # Bulk insert data
                    session.bulk_insert_mappings(TableClass, records)
                    session.commit()
                    print(f"Loaded data into table '{table_name}' in schema '{schema}'.")

    # Close session
    session.close()

print("Data loading completed for all schemas.")
