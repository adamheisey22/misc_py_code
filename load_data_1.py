import os
import pandas as pd
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import importlib

# Database connection settings
DB_USER = "your_username"
DB_PASSWORD = "your_password"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "your_database"

# Create the database engine
DB_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
try:
    engine = create_engine(DB_URL)
    connection = engine.connect()
    print("✅ Connected to PostgreSQL successfully!")
except Exception as e:
    print(f"❌ Failed to connect to the database: {e}")
    exit(1)

# Define schemas and corresponding ORM definition modules
SCHEMA_DEFINITIONS = {
    "electricity": "elec_definitions",
    "hydrogen": "hydro_definitions",
    "integrator": "integ_definitions",
    "residential": "res_definitions",
}

# Iterate over schemas and load data
for schema, module_name in SCHEMA_DEFINITIONS.items():
    folder_path = schema  # Folder name matches schema

    try:
        # Import the corresponding ORM definition module dynamically
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError:
            print(f"❌ Error: Definition module '{module_name}' not found. Skipping schema '{schema}'.")
            continue  # Skip this schema if module is missing

        Base = module.Base
        Session = sessionmaker(bind=engine)  # Use the common engine
        session = Session()

        # ✅ Ensure the tables are created before inserting data
        Base.metadata.create_all(engine)
        print(f"✅ Tables created for schema '{schema}' (if they didn't already exist).")

        # Get table mappings from ORM definitions
        table_classes = {cls.__tablename__: cls for cls in Base.__subclasses__()}

        # Check if folder exists
        if not os.path.exists(folder_path):
            print(f"⚠️ Warning: Folder '{folder_path}' does not exist. Skipping schema '{schema}'.")
            continue

        # Iterate over CSV files and load data into PostgreSQL
        for filename in os.listdir(folder_path):
            if filename.endswith(".csv"):
                table_name = filename.replace(".csv", "").lower()
                file_path = os.path.join(folder_path, filename)

                # Check if the corresponding table class exists
                if table_name in table_classes:
                    TableClass = table_classes[table_name]
                    df = pd.read_csv(file_path)

                    if df.empty:
                        print(f"⚠️ Warning: CSV '{filename}' is empty. Skipping.")
                        continue

                    # Convert dataframe to a list of dictionaries for ORM bulk insert
                    records = df.to_dict(orient="records")

                    # Bulk insert data
                    session.bulk_insert_mappings(TableClass, records)
                    session.commit()
                    print(f"✅ Loaded data into table '{table_name}' in schema '{schema}'.")

                else:
                    print(f"⚠️ Warning: Table '{table_name}' is not defined in ORM. Skipping.")

        # Close session for this schema
        session.close()

    except Exception as e:
        print(f"❌ Error processing schema '{schema}': {e}")

# Close the database connection
connection.close()
print("🚀 Data loading completed for all schemas.")
