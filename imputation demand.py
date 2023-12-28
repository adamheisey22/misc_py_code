import pandas as pd
import numpy as np

def impute_demand_optimized(df):
    # Assuming df has columns: 'demand', 'demand_forecast', 'no_forecast', 'lower_threshold', 'upper_threshold'

    def valid_demand(value, lower_threshold, upper_threshold):
        return lower_threshold <= value <= upper_threshold

    # Rule 1: Check if demand is missing or out of range, and demand forecast is available
    condition_1 = (df['demand'].isnull() | ~df.apply(lambda x: valid_demand(x['demand'], x['lower_threshold'], x['upper_threshold']), axis=1)) & (df['no_forecast'] != True) & ~(df['demand_forecast'].isnull()) & df.apply(lambda x: valid_demand(x['demand_forecast'], x['lower_threshold'], x['upper_threshold']), axis=1)
    df.loc[condition_1, 'demand'] = df.loc[condition_1, 'demand_forecast']

    # Rule 2: Check if demand is still missing or out of range, and prior hour demand is available
    condition_2 = (df['demand'].isnull() | ~df.apply(lambda x: valid_demand(x['demand'], x['lower_threshold'], x['upper_threshold']), axis=1)) & ~(df['demand'].shift(1).isnull()) & df.apply(lambda x: valid_demand(x['demand'].shift(1), x['lower_threshold'], x['upper_threshold']), axis=1)
    df.loc[condition_2, 'demand'] = df.loc[condition_2, 'demand'].shift(1)

    # Rule 3: Check if demand is still missing or out of range, and prior day demand is available
    condition_3 = (df['demand'].isnull() | ~df.apply(lambda x: valid_demand(x['demand'], x['lower_threshold'], x['upper_threshold']), axis=1)) & ~(df['demand'].shift(24).isnull()) & df.apply(lambda x: valid_demand(x['demand'].shift(24), x['lower_threshold'], x['upper_threshold']), axis=1)
    df.loc[condition_3, 'demand'] = df.loc[condition_3, 'demand'].shift(24)

    # Rule 4: Set to 0 if still missing or out of range
    df['demand'].fillna(0, inplace=True)

    return df

# Example usage:
# df = ...  # Your DataFrame with the required columns
# df_imputed = impute_demand_optimized(df)
