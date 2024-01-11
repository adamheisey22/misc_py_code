import pandas as pd
from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from time import time
import datetime

# Define the base class for ORM
Base = declarative_base()

# ORM class definitions
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

def check_data_exists(session, model, id_value):
    """
    Check if data with the specific id exists in the table.
    """
    return session.query(model).filter(model.id == id_value).first() is not None

def EIA930_BA_download(years, session):
    for year in years:
        urls = [
            f'https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/EIA930_BALANCE_{year}_Jul_Dec.csv',
            f'https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/EIA930_BALANCE_{year}_Jan_Jun.csv'
        ]

        for url in urls:
            try:
                df = pd.read_csv(url, low_memory=False)
                df = convert_to_datetime(df, 'UTC Time at End of Hour')
                df['id'] = df['Balancing Authority'] + '_' + df['UTC Time at End of Hour'].astype(str)

                for _, row in df.iterrows():
                    if not check_data_exists(session, EIA930Balance, row['id']):
                        session.add(EIA930Balance(**row.to_dict()))
                
                session.commit()
            except Exception as e:
                print(f"Error downloading or processing data for year {year} from {url}: {e}")
                session.rollback()

def EIA930_SUB_download(years, session):
    for year in years:
        urls = [
            f'https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/EIA930_SUBREGION_{year}_Jul_Dec.csv',
            f'https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/EIA930_SUBREGION_{year}_Jan_Jun.csv'
        ]

        for url in urls:
            try:
                df = pd.read_csv(url, low_memory=False)
                df = convert_to_datetime(df, 'UTC Time at End of Hour')
                df['id'] = df['Sub-Region'] + '_' + df['UTC Time at End of Hour'].astype(str)

                for _, row in df.iterrows():
                    if not check_data_exists(session, EIA930Subregion, row['id']):
                        session.add(EIA930Subregion(**row.to_dict()))
                
                session.commit()
            except Exception as e:
                print(f"Error downloading or processing data for year {year} from {url}: {e}")
                session.rollback()

def main():
    engine = create_engine('sqlite:///C:/Users/adamh/OneDrive - Marquette University/Personal/Jobs/Health Catalyst/EIA930_database.db')
    Session = sessionmaker(bind=engine)
    session = Session()

    create_database(engine)

    t0 = time()

    # Define years for each function
    ba_years = [2018, 2019, 2020, 2021, 2022, 2023]
    subregion_years = [2019, 2020, 2021, 2022, 2023]

    # Perform downloads for each function with its respective years
    EIA930_BA_download(ba_years, session)
    EIA930_SUB_download(subregion_years, session)

    t1 = time()
    print("Time taken:", str(datetime.timedelta(seconds=round(t1 - t0))))

    session.close()

if __name__ == "__main__":
    main()
