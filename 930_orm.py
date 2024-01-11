import pandas as pd
from sqlalchemy import create_engine, Column, String, DateTime, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import support_functions
from time import time
import datetime
import requests

# Define the base class for ORM
Base = declarative_base()

# ORM class definitions as before
class EIA930Balance(Base):
    __tablename__ = 'eia930_balance_raw'
    id = Column(String, primary_key=True)
    balancing_authority = Column(String)
    utc_time_at_end_of_hour = Column(DateTime)
    # Add other columns as needed

class EIA930Subregion(Base):
    __tablename__ = 'eia930_subregion_raw'
    id = Column(String, primary_key=True)
    subregion = Column(String)
    utc_time_at_end_of_hour = Column(DateTime)
    # Add other columns as needed

def create_database(engine):
    Base.metadata.create_all(engine)

def convert_to_datetime(df, column_name):
    """
    Convert a DataFrame column to datetime objects.
    """
    df[column_name] = pd.to_datetime(df[column_name])
    return df

def check_data_exists(session, model, year):
    """
    Check if data for the specific year exists in the table.
    """
    return session.query(model).filter(model.utc_time_at_end_of_hour.between(f'{year}-01-01', f'{year}-12-31')).first() is not None

def EIA930_BA_download(years, session):
    for year in years:
        if check_data_exists(session, EIA930Balance, year):
            print(f"Data for year {year} already exists in EIA930 Balance. Skipping download.")
            continue
        
        urls = [
            f'https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/EIA930_BALANCE_{year}_Jul_Dec.csv',
            f'https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/EIA930_BALANCE_{year}_Jan_Jun.csv'
        ]

        for url in urls:
            try:
                df = pd.read_csv(url, low_memory=False)
                df = convert_to_datetime(df, 'UTC Time at End of Hour')
                df['id'] = df['Balancing Authority'] + '_' + df['UTC Time at End of Hour'].astype(str)

                # Bulk insert to optimize performance
                session.bulk_insert_mappings(EIA930Balance, df.to_dict(orient='records'))
                session.commit()
            except Exception as e:
                print(f"Error downloading or processing data for year {year} from {url}: {e}")
                session.rollback()

def EIA930_SUB_download(years, session):
    for year in years:
        if check_data_exists(session, EIA930Subregion, year):
            print(f"Data for year {year} already exists in EIA930 Subregion. Skipping download.")
            continue
        
        urls = [
            f'https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/EIA930_SUBREGION_{year}_Jul_Dec.csv',
            f'https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/EIA930_SUBREGION_{year}_Jan_Jun.csv'
        ]

        for url in urls:
            try:
                df = pd.read_csv(url, low_memory=False)
                df = convert_to_datetime(df, 'UTC Time at End of Hour')
                df['id'] = df['Subregion'] + '_' + df['UTC Time at End of Hour'].astype(str)

                # Bulk insert to optimize performance
                session.bulk_insert_mappings(EIA930Subregion, df.to_dict(orient='records'))
                session.commit()
            except Exception as e:
                print(f"Error downloading or processing data for year {year} from {url}: {e}")
                session.rollback()

def main():
    engine = create_engine('sqlite:///N:/NextGen Developers/Projects/demand_profiles/EIA930_database.db')
    Session = sessionmaker(bind=engine)
    session = Session()

    create_database(engine)

    t0 = time()

    # Define years for each function
    ba_years = [2018, 2019, 2020]
    subregion_years = [2021, 2022, 2023]

    # Perform downloads for each function with its respective years
    EIA930_BA_download(ba_years, session)
    EIA930_SUB_download(subregion_years, session)

    t1 = time()
    print(str(datetime.timedelta(seconds=round(t1 - t0))))

    session.close()

if __name__ == "__main__":
    main()
