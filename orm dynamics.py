import pandas as pd
from textwrap import dedent

# Example dataframes setup
# Replace these with your actual dataframes
df1 = pd.DataFrame({
    'day': pd.to_datetime(['2021-01-01', '2021-01-02', '2021-01-03']),
    'value': [10, 20, 30]
}).set_index(pd.Index([1, 2, 3], name='pt'))

df2 = pd.DataFrame({
    'day': pd.to_datetime(['2021-02-01', '2021-02-02', '2021-02-03']),
    'value': [100, 200, 300]
}).set_index(pd.Index([1, 2, 3], name='y'))

dataframes = {'Table1': df1, 'Table2': df2}

def generate_class_definition(table_name, df):
    class_name = table_name
    index_col = df.index.name
    fields = []
    
    # Adding primary key
    if index_col is not None:
        dtype = 'Integer'
        if pd.api.types.is_float_dtype(df.index.dtype):
            dtype = 'Float'
        elif pd.api.types.is_string_dtype(df.index.dtype):
            dtype = 'String'
        fields.append(f"{index_col} = Column({dtype}, primary_key=True)")

    # Adding other columns
    for col in df.columns:
        if col == 'day':
            fields.append(f"{col} = Column(Date)")
        elif pd.api.types.is_float_dtype(df[col].dtype):
            fields.append(f"{col} = Column(Float)")
        elif pd.api.types.is_integer_dtype(df[col].dtype):
            fields.append(f"{col} = Column(Integer)")
        else:
            fields.append(f"{col} = Column(String)")

    # Compose the class definition
    fields_str = "\n    ".join(fields)
    class_definition = f"""
class {class_name}(Base):
    __tablename__ = '{table_name.lower()}'
    {fields_str}
    """
    return class_definition

# Write definitions to a .py file
with open('database_models.py', 'w') as f:
    f.write("from sqlalchemy import create_engine, Column, Integer, Float, String, Date\n")
    f.write("from sqlalchemy.ext.declarative import declarative_base\n")
    f.write("from sqlalchemy.orm import sessionmaker\n")
    f.write("Base = declarative_base()\n\n")
    
    for table_name, df in dataframes.items():
        class_def = generate_class_definition(table_name, df)
        f.write(dedent(class_def))
    
    f.write("\n# Database setup\n")
    f.write("engine = create_engine('sqlite:///mydatabase.db')\n")
    f.write("Base.metadata.create_all(engine)\n\n")
    f.write("# If you need to interact with the database\n")
    f.write("Session = sessionmaker(bind=engine)\n")
    f.write("session = Session()\n\n")
    f.write("# Add data handling below as required\n")
    f.write("session.close()\n

# Assuming this code is added at the end of 'database_models.py'
def load_data_to_db(session, table_class, dataframe):
    # Iterate over the rows of the DataFrame
    for index, row in dataframe.iterrows():
        # Convert the row to a dictionary, including the index
        data_dict = row.to_dict()
        data_dict[dataframe.index.name] = index
        # Create an instance of the table class
        obj = table_class(**data_dict)
        # Add to the session
        session.add(obj)
    # Commit the transaction
    session.commit()

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Dictionary of DataFrames, assumed to already be defined
# dataframes = {'Table1': df1, 'Table2': df2} - defined earlier in your script
key_list = dataframes.keys()  # or any list of keys that represents the tables you have

# Load data for each table listed in key_list
for table_name in key_list:
    # Retrieve the table class dynamically using globals()
    table_class = globals()[table_name]
    # Retrieve the dataframe associated with the table
    dataframe = dataframes[table_name]
    # Load data to database
    load_data_to_db(session, table_class, dataframe)

# Close the session when done
session.close()

print("Data has been loaded into the database.")



####new

def create_unique_id(df):
    # Temporarily rename the index to avoid conflicts
    temp_index_name = df.index.name if df.index.name is not None else 'index'
    # Ensure the temporary index name does not conflict with existing columns
    while temp_index_name in df.columns:
        temp_index_name += '_temp'

    df.index.rename(temp_index_name, inplace=True)
    df_reset = df.reset_index()  # Now resetting the index should not cause conflicts
    # Create the 'id' by concatenating all column values into a single string
    df_reset['id'] = df_reset.apply(lambda row: '-'.join(row.astype(str)), axis=1)
    # Set the 'id' column as the new index
    df_final = df_reset.set_index('id')
    # Restore the original index name if it was changed
    if df.index.name != df.index.name:
        df.index.rename(df.index.name, inplace=True)
    return df_final

# Example usage
df1 = pd.DataFrame({
    'pt': [1, 2, 3],
    'day': pd.to_datetime(['2021-01-01', '2021-01-02', '2021-01-03']),
    'value': [10, 20, 30]
}).set_index('pt')

df2 = pd.DataFrame({
    'y': [1, 2, 3],
    'day': pd.to_datetime(['2021-02-01', '2021-02-02', '2021-02-03']),
    'value': [100, 200, 300]
}).set_index('y')

dataframes = {'Table1': df1, 'Table2': df2}

for key, df in dataframes.items():
    dataframes[key] = create_unique_id(df)
