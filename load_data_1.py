import os
import pandas as pd
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import importlib

# Folder location for electricity data
FOLDER_PATH = "electricity"

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
    print("Connected to PostgreSQL successfully!")
except Exception as e:
    print(f"Failed to connect to the database: {e}")
    exit(1)

# Import electricity ORM definitions
try:
    module = importlib.import_module("elec_definitions")
    Base = module.Base
    Session = sessionmaker(bind=engine)  # Use the common engine
    session = Session()

    # Get table mappings from ORM definitions
    table_classes = {cls.__tablename__: cls for cls in Base.__subclasses__()}

    # Check if folder exists
    if os.path.exists(FOLDER_PATH):
        for filename in os.listdir(FOLDER_PATH):
            if filename.endswith(".csv"):
                table_name = filename.replace(".csv", "").lower()
                file_path = os.path.join(FOLDER_PATH, filename)

                # Check if the corresponding table class exists
                if table_name in table_classes:
                    TableClass = table_classes[table_name]
                    df = pd.read_csv(file_path)

                    # Convert dataframe to a list of dictionaries for ORM bulk insert
                    records = df.to_dict(orient="records")

                    # Bulk insert data
                    session.bulk_insert_mappings(TableClass, records)
                    session.commit()
                    print(f"Loaded data into table '{table_name}' in schema 'electricity'.")

    # Close session
    session.close()

except Exception as e:
    print(f"Error loading data into electricity schema: {e}")

# Close the database connection
connection.close()
print("Electricity data loading completed.")
