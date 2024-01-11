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
    df[column_name] = pd.to_datetime(df[column_name])
    return df

def check_data_exists(session, model, id_list):
    existing_ids = session.query(model.id).filter(model.id.in_(id_list)).all()
    return [id[0] for id in existing_ids]

def EIA930_BA_download(years, session):
    desired_columns = {
        'Balancing Authority': 'balancing_authority', 
        'UTC Time at End of Hour': 'utc_time_at_end_of_hour',
        # Add other desired columns here
    }
    for year in years:
        urls = [
            f'https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/EIA930_BALANCE_{year}_Jul_Dec.csv',
            f'https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/EIA930_BALANCE_{year}_Jan_Jun.csv'
        ]

        for url in urls:
            try:
                df = pd.read_csv(url, usecols=desired_columns.keys(), low_memory=False)
                df = convert_to_datetime(df, 'UTC Time at End of Hour')
                df.rename(columns=desired_columns, inplace=True)
                df['id'] = df['balancing_authority'] + '_' + df['utc_time_at_end_of_hour'].astype(str)

                # Check and remove existing data
                existing_ids = check_data_exists(session, EIA930Balance, df['id'].tolist())
                df = df[~df['id'].isin(existing_ids)]

                # Perform bulk insert
                if not df.empty:
                    session.bulk_insert_mappings(EIA930Balance, df.to_dict(orient='records'))
                    session.commit()

            except Exception as e:
                print(f"Error downloading or processing data for year {year} from {url}: {e}")
                session.rollback()

# Similar function for EIA930Subregion can be implemented

def main():
    engine = create_engine('sqlite:///C:/Users/adamh/OneDrive - Marquette University/Personal/Jobs/Health Catalyst/EIA930_database.db')
    Session = sessionmaker(bind=engine)
    session = Session()

    create_database(engine)

    t0 = time()

    ba_years = [2018, 2019, 2020, 2021, 2022, 2023]
    subregion_years = [2019, 2020, 2021, 2022, 2023]

    EIA930_BA_download(ba_years, session)
    # EIA930_SUB_download(subregion_years, session) - implement similarly

    t1 = time()
    print("Time taken:", str(datetime.timedelta(seconds=round(t1 - t0))))

    session.close()

if __name__ == "__main__":
    main()
