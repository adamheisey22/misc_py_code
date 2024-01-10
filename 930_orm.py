import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, String, select, func, inspect
from sqlalchemy.exc import NoSuchTableError
# import support_functions
from time import time
import datetime

def create_engine_with_db(database_url):
    return create_engine(database_url)

def get_or_create_table(engine, table_name, dataframe):
    meta = MetaData()
    inspector = inspect(engine)

    if not inspector.has_table(table_name):
        # Create table if it doesn't exist
        columns = [Column(name, String) for name in dataframe.columns]
        table = Table(table_name, meta, *columns)
        meta.create_all(engine)
    else:
        table = Table(table_name, meta, autoload_with=engine)

    return table

def update_table_structure(engine, table, dataframe):
    meta = MetaData()
    meta.reflect(bind=engine)
    existing_columns = set(table.columns.keys())
    new_columns = set(dataframe.columns) - existing_columns

    with engine.connect() as conn:
        for column in new_columns:
            # SQLite requires columns to be quoted if they contain special characters or spaces
            quoted_column = f'"{column}"' if ' ' in column or any(c in column for c in '()[]{}<>-+=*%&^$#@!~') else column
            conn.execute(f'ALTER TABLE {table.name} ADD COLUMN {quoted_column} STRING')

def data_exists(engine, table_name, year, date_column):
    meta = MetaData(engine)
    table = Table(table_name, meta, autoload=True)

    if date_column not in table.c:
        print(f"Column '{date_column}' not found in the table '{table_name}'.")
        return False

    query = select([func.count()]).select_from(table).where(table.c[date_column].like(f'%{year}%'))
    result = engine.execute(query).scalar()
    return result > 0

def download_data(url):
    try:
        dataframe = pd.read_csv(url, low_memory=False, on_bad_lines='skip')
        print(f"Columns in {url}: {dataframe.columns.tolist()}")
        return dataframe
    except pd.errors.ParserError as e:
        print(f"Parser error while reading {url}: {e}")
        return None

def process_and_load_data(years, url_template, table_name, engine, date_column):
    for year in years:
        for half in ['Jan_Jun', 'Jul_Dec']:
            url = url_template.format(year=year, half=half)
            dataframe = download_data(url)

            if dataframe is not None:
                table = get_or_create_table(engine, table_name, dataframe)
                update_table_structure(engine, table, dataframe)

                if not data_exists(engine, table_name, year, date_column):
                    dataframe.to_sql(table_name, con=engine, index=False, if_exists='append')
                    print(f'Data from {url} loaded into {table_name}.')
            else:
                print(f"Failed to download or parse data from {url}")

def main():
    # log_file = support_functions.log_output("outputs/download_logs/eia930/")
    try:
        t0 = time()

        database_url = 'sqlite:///C:/Users/adamh/OneDrive - Marquette University/Personal/Jobs/Health Catalyst/EIA930_database.db'
        engine = create_engine_with_db(database_url)

        years = [2018, 2019, 2020, 2021, 2022, 2023]
        url_template_balance = 'https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/EIA930_BALANCE_{year}_{half}.csv'
        url_template_subregion = 'https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/EIA930_SUBREGION_{year}_{half}.csv'

        process_and_load_data(years, url_template_balance, 'eia930_balance_raw', engine, 'Data Date')
        process_and_load_data(years, url_template_subregion, 'eia930_subregion_raw', engine, 'Data Date')

        t1 = time()
        print(str(datetime.timedelta(seconds=round(t1 - t0))))

    finally:
        print('dn')
        # log_file.close()

if __name__ == "__main__":
    main()