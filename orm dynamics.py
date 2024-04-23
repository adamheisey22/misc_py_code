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
