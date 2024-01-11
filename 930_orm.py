import pandas as pd
from sqlalchemy import create_engine, Column, String, DateTime, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# import support_functions
from time import time
import datetime

# Define the base class for ORM
Base = declarative_base()

# Example class for EIA930 Balance
class EIA930Balance(Base):
    __tablename__ = 'eia930_balance_raw'
    id = Column(String, primary_key=True)
    balancing_authority = Column(String)
    utc_time_at_end_of_hour = Column(DateTime)
    # Add other columns as needed, matching the CSV file structure

# Example class for EIA930 Subregion
class EIA930Subregion(Base):
    __tablename__ = 'eia930_subregion_raw'
    id = Column(String, primary_key=True)
    subregion = Column(String)
    utc_time_at_end_of_hour = Column(DateTime)
    # Add other columns as needed, matching the CSV file structure

def create_database(engine):
    Base.metadata.create_all(engine)

def convert_to_datetime(df, column_name):
    """
    Convert a DataFrame column to datetime objects
    """
    df[column_name] = pd.to_datetime(df[column_name])
    return df

def EIA930_BA_download(years, session):
    for year in years:
        url_jul_dec = f'https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/EIA930_BALANCE_{year}_Jul_Dec.csv'
        url_jan_jun = f'https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/EIA930_BALANCE_{year}_Jan_Jun.csv'

        for url in [url_jan_jun, url_jul_dec]:
            df = pd.read_csv(url, low_memory=False)
            df = convert_to_datetime(df, 'UTC Time at End of Hour')
            df['id'] = df['Balancing Authority'] + '_' + df['UTC Time at End of Hour'].astype(str)

            data_to_insert = df.to_dict(orient='records')
            for record in data_to_insert:
                balance_record = EIA930Balance(
                    id=record['id'],
                    balancing_authority=record['Balancing Authority'],
                    utc_time_at_end_of_hour=record['UTC Time at End of Hour']
                    # Map other fields as necessary
                )
                session.add(balance_record)
            session.commit()

def EIA930_SUB_download(years, session):
    for year in years:
        url_jul_dec = f'https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/EIA930_SUBREGION_{year}_Jul_Dec.csv'
        url_jan_jun = f'https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/EIA930_SUBREGION_{year}_Jan_Jun.csv'

        for url in [url_jan_jun, url_jul_dec]:
            df = pd.read_csv(url, low_memory=False)
            df = convert_to_datetime(df, 'UTC Time at End of Hour')
            df['id'] = df['Sub-Region'] + '_' + df['UTC Time at End of Hour'].astype(str)

            data_to_insert = df.to_dict(orient='records')
            for record in data_to_insert:
                subregion_record = EIA930Subregion(
                    id=record['id'],
                    subregion=record['Sub-Region'],
                    utc_time_at_end_of_hour=record['UTC Time at End of Hour']
                    # Map other fields as necessary
                )
                session.add(subregion_record)
            session.commit()

def main():
    engine = create_engine('sqlite:///C:/Users/adamh/OneDrive - Marquette University/Personal/Jobs/Health Catalyst/EIA930_database.db')
    Session = sessionmaker(bind=engine)
    session = Session()

    create_database(engine)

    t0 = time()

    years_to_download = [2019, 2020, 2021, 2022, 2023]
    EIA930_BA_download(years_to_download, session)
    EIA930_SUB_download(years_to_download, session)

    t1 = time()
    print(str(datetime.timedelta(seconds=round(t1 - t0))))

    session.close()

if __name__ == "__main__":
    main()
