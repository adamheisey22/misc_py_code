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
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from models import Base, Table1, Table2  # Import your table definitions

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
Base.metadata.create_all(engine)  # Make sure Base is imported from models
Session = sessionmaker(bind=engine)
session = Session()

# Example DataFrame creation
dataframes = {
    'Table1': pd.DataFrame({
        'id': [1, 2, 3],
        'name': ['Alice', 'Bob', 'Cathy'],
        'date': pd.to_datetime(['2021-01-01', '2021-02-01', '2021-03-01'])
    }),
    'Table2': pd.DataFrame({
        'id': [4, 5, 6],
        'description': ['Desc1', 'Desc2', 'Desc3'],
        'created_on': pd.to_datetime(['2022-01-01', '2022-02-01', '2022-03-01'])
    })
}

# Define a mapping of DataFrame names to table classes explicitly
table_mapping = {
    'Table1': Table1,
    'Table2': Table2,
    # Add other table class mappings here
}

# Load data using the mapping
for table_name, table_class in table_mapping.items():
    dataframe = dataframes[table_name]
    load_data_to_db(session, table_class, dataframe)

session.close()
print("Data has been loaded into the database.")
