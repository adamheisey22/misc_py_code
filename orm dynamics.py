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
def prepare_dates(df):
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = pd.to_datetime(df[col]).dt.date
    return df

def load_data_to_db(session, table_class, dataframe):
    # Prepare date columns
    dataframe = prepare_dates(dataframe)
    
    for index, row in dataframe.iterrows():
        data_dict = row.to_dict()
        data_dict[dataframe.index.name] = index
        obj = table_class(**data_dict)
        session.add(obj)
    session.commit()

# Initialize database and session
engine = create_engine('sqlite:///mydatabase.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Load data to database
for table_name in dataframes:
    table_class = globals()[table_name]
    dataframe = dataframes[table_name]
    load_data_to_db(session, table_class, dataframe)

session.close()
print("Data has been loaded into the database.")
