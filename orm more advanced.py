from sqlalchemy import Table, select
from sqlalchemy.orm import sessionmaker

def yearQuery(year, engine, metadata, w_col, l_stationID_fil):
    # Dynamically define the table name
    table_name = f"noaa_hourly_data_{year}"

    # Reflect the table structure from the database
    table = Table(table_name, metadata, autoload_with=engine)

    # Prepare the column list for the query
    columns_to_select = [
        table.c.id,
        table.c.DATE,
        table.c.station_id,
    ] + [table.c[col] for col in w_col]  # Dynamically add columns specified in w_col

    # Construct the query using the SQLAlchemy Table object
    query = select(columns_to_select).where(table.c.station_id.in_(l_stationID_fil))

    # Execute the query and fetch the result
    with engine.connect() as connection:
        result = connection.execute(query)
        df = pd.read_sql(query, connection)

    return df
