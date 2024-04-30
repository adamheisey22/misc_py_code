import pandas as pd
from textwrap import dedent
from sqlalchemy import create_engine, Column, Integer, Float, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

def generate_class_definition(table_name, df):
    class_name = table_name
    index_col = df.index.name
    fields = []
    
    if index_col is not None:
        dtype = 'Integer'
        if pd.api.types.is_float_dtype(df.index.dtype):
            dtype = 'Float'
        elif pd.api.types.is_string_dtype(df.index.dtype):
            dtype = 'String'
        fields.append(f"{index_col} = Column({dtype}, primary_key=True)")

    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            fields.append(f"{col} = Column(Date)")
        elif pd.api.types.is_float_dtype(df[col].dtype):
            fields.append(f"{col} = Column(Float)")
        elif pd.api.types.is_integer_dtype(df[col].dtype):
            fields.append(f"{col} = Column(Integer)")
        else:
            fields.append(f"{col} = Column(String)")

    fields_str = "\n    ".join(fields)
    class_definition = f"""
class {class_name}(Base):
    __tablename__ = '{table_name.lower()}'
    {fields_str}
    """
    return class_definition





##next
import inspect
from models import Base  # Assuming models.py contains Base and all table definitions

def create_table_mapping(module):
    """
    Creates a mapping of table names to their SQLAlchemy class definitions
    found in the given module. Assumes that each table class inherits from `Base`
    and that the primary key column is named 'id'.
    
    Args:
    - module: A module containing SQLAlchemy table class definitions.

    Returns:
    - A dictionary mapping table class names to their class definitions.
    """
    mapping = {}
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and issubclass(obj, Base) and obj.__tablename__:
            mapping[obj.__tablename__] = obj
    return mapping

# Use the function to create the table mapping
table_mapping = create_table_mapping(models)


import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
import models  # Import your module with table definitions
from models import Base

def prepare_dates(df):
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = pd.to_datetime(df[col]).dt.date
    return df

def load_data_to_db(session, table_class, dataframe):
    dataframe = prepare_dates(dataframe)
    for index, row in dataframe.iterrows():
        data_dict = row.to_dict()
        if dataframe.index.name:
            data_dict[dataframe.index.name] = index

        exists = session.query(table_class).filter_by(id=data_dict['id']).first()
        if not exists:
            try:
                obj = table_class(**data_dict)
                session.add(obj)
                session.commit()
            except IntegrityError:
                session.rollback()
        else:
            print(f"Entry with id = {data_dict['id']} already exists and was not added.")

# Initialize database and session
engine = create_engine('sqlite:///mydatabase.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Use the function to create the table mapping
table_mapping = create_table_mapping(models)

# Example DataFrame creation and loading
dataframes = {
    'table1': pd.DataFrame({
        'id': [1, 2, 3],
        'name': ['Alice', 'Bob', 'Cathy'],
        'date': pd.to_datetime(['2021-01-01', '2021-02-01', '2021-03-01'])
    }),
    'table2': pd.DataFrame({
        'id': [4, 5, 6],
        'description': ['Desc1', 'Desc2', 'Desc3'],
        'created_on': pd.to_datetime(['2022-01-01', '2022-02-01', '2022-03-01'])
    })
}

# Load data using the mapping
for table_name, table_class in table_mapping.items():
    dataframe = dataframes[table_name]
    load_data_to_db(session, table_class, dataframe)

session.close()
print("Data has been loaded into the database.")


#new
import pandas as pd
from sqlalchemy import create_engine, Column, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import models  # This is your module with ORM definitions
import inspect

# Function to prepare date columns
def prepare_dates(df):
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = pd.to_datetime(df[col]).dt.date
    return df

# Function to load data into database efficiently
def load_data_to_db(session, table_class, dataframe):
    dataframe = prepare_dates(dataframe)
    # Convert DataFrame to list of dictionaries suitable for batch insert
    data_records = dataframe.to_dict(orient='records')
    # Bulk insert all records at once
    session.bulk_insert_mappings(table_class, data_records)
    session.commit()

# Define Base for ORM classes
Base = declarative_base()

# Initialize database and session
engine = create_engine('sqlite:///mydatabase.db')
Base.metadata.drop_all(engine)  # Drop all tables
Base.metadata.create_all(engine)  # Create all tables

# Session creation
Session = sessionmaker(bind=engine)
session = Session()

# Automatically create table_classes dictionary from models module
table_classes = {cls.__name__: cls for name, cls in inspect.getmembers(models, inspect.isclass)
                 if issubclass(cls, Base) and cls is not Base}

# Dictionary of DataFrames (example usage)
dataframes = {
    'ExampleTable': pd.DataFrame({'date': ['2023-01-01'], 'value': [100]}),
    # Add other dataframes here
}

# Load data to database
for table_name, dataframe in dataframes.items():
    if table_name in table_classes:
        table_class = table_classes[table_name]
        load_data_to_db(session, table_class, dataframe)

session.close()
print("Data has been loaded into the database.")



####NEW
import pandas as pd
from sqlalchemy import create_engine, Column, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import models  # Assumes all ORM classes are defined here
import inspect

Base = declarative_base()

def prepare_dates(df):
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = pd.to_datetime(df[col]).dt.date
    return df

def load_data_to_db(session, table_class, dataframe):
    try:
        dataframe = prepare_dates(dataframe)
        data_records = dataframe.to_dict(orient='records')
        if data_records:  # Ensure there is data to insert
            session.bulk_insert_mappings(table_class, data_records)
            session.commit()
            print(f"Data successfully loaded into {table_class.__tablename__}.")
        else:
            print(f"No data to load for {table_class.__tablename__}.")
    except Exception as e:
        session.rollback()
        print(f"Error loading data into {table_class.__tablename__}: {e}")
    finally:
        session.close()

# Database initialization
engine = create_engine('sqlite:///mydatabase.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

# Automatically generate table_classes from models
table_classes = {cls.__name__: cls for name, cls in inspect.getmembers(models, inspect.isclass)
                 if issubclass(cls, Base) and cls is not Base}

# Example DataFrame dictionary
dataframes = {
    'ExampleTable': pd.DataFrame({'date': ['2023-01-01'], 'value': [100]}),
    # Ensure these DataFrames are properly populated
}

# Load data
for table_name, dataframe in dataframes.items():
    if table_name in table_classes:
        with Session() as session:
            table_class = table_classes[table_name]
            load_data_to_db(session, table_class, dataframe)

print("Database operations completed.")


##try this
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
import models  # Import your module with table definitions
from models import Base

def prepare_dates(df):
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = pd.to_datetime(df[col]).dt.date
    return df

def load_data_to_db(session, table_class, dataframe):
    dataframe = prepare_dates(dataframe)
    for index, row in dataframe.iterrows():
        data_dict = row.to_dict()
        if dataframe.index.name:
            data_dict[dataframe.index.name] = index

        # Check for existence using the primary key (id), avoiding the costly query operation
        obj = table_class(**data_dict)
        session.merge(obj)  # `merge` instead of `add` will check and update if exists, otherwise insert

    try:
        session.commit()  # Commit all the operations as a batch
    except IntegrityError:
        session.rollback()

# Initialize database and session
engine = create_engine('sqlite:///mydatabase.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Use the function to create the table mapping
table_mapping = create_table_mapping(models)

# Example DataFrame creation and loading
dataframes = {
    'table1': pd.DataFrame({
        'id': [1, 2, 3],
        'name': ['Alice', 'Bob', 'Cathy'],
        'date': pd.to_datetime(['2021-01-01', '2021-02-01', '2021-03-01'])
    }),
    'table2': pd.DataFrame({
        'id': [4, 5, 6],
        'description': ['Desc1', 'Desc2', 'Desc3'],
        'created_on': pd.to_datetime(['2022-01-01', '2022-02-01', '2022-03-01'])
    })
}

# Load data using the mapping
for table_name, table_class in table_mapping.items():
    dataframe = dataframes[table_name]
    load_data_to_db(session, table_class, dataframe)

session.close()
print("Data has been loaded into the database.")
