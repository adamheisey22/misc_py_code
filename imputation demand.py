import pandas as pd
import numpy as np

def fill_demand_ba(df):
    # Convert relevant columns to numeric
    df[['Demand', 'demand_forecast', 'Lower_Threshold', 'Upper_Threshold', 'Hour']] = df[['Demand', 'demand_forecast', 'Lower_Threshold', 'Upper_Threshold', 'Hour']].apply(pd.to_numeric, errors='coerce')

    # Convert 'Date' to datetime format
    df['Date'] = pd.to_datetime(df['Date'])

    df.sort_values(by=['BA', 'Date', 'Hour'], inplace=True)

    # Read exception lookup table for BAs
    df_exception = pd.read_csv('ba_no_forec_lkup_table.csv')
    exception_list = set(df_exception['BA'])

    # Check for valid demand or if it's within the threshold
    df['valid_demand'] = df.apply(lambda row: row['Demand'] if pd.notna(row['Demand']) and (row['Lower_Threshold'] <= row['Demand'] <= row['Upper_Threshold']) else np.nan, axis=1)

    # Function to impute demand
    def impute_demand(row, exc_mask):
        if pd.isna(row['valid_demand']):
            if not exc_mask[row.name] and pd.notna(row['demand_forecast']):
                return row['demand_forecast']
            else:
                return np.nan
        else:
            return row['valid_demand']

    # Apply imputation logic
    df['fill_demand'] = df.apply(lambda row: impute_demand(row, df['BA'].isin(exception_list)), axis=1)

    # Forward fill from previous hour and then from the same hour previous day
    df['fill_demand'] = df.groupby('BA')['fill_demand'].transform(lambda x: x.fillna(method='ffill', limit=1))
    df['fill_demand'] = df.groupby('BA')['fill_demand'].transform(lambda x: x.fillna(x.shift(24)))

    # Fill remaining NaNs with 0
    df['fill_demand'].fillna(0, inplace=True)

    return df

# Apply the function
df_imp = fill_demand_ba(df_out)
