import pandas as pd
import numpy as np

def fill_demand_ba(df):
    # Convert relevant columns to numeric
    cols_to_convert = ['Demand', 'demand_forecast']
    df[cols_to_convert] = df[cols_to_convert].apply(pd.to_numeric, errors='coerce')

    # Convert 'Date' to datetime format and sort
    df['Date'] = pd.to_datetime(df['Date'])
    df.sort_values(by=['BA', 'Date', 'Hour'], inplace=True)

    # Compute thresholds for each BA
    thresholds = df.groupby('BA')['Demand'].agg(['mean', 'std']).reset_index()
    thresholds['Lower_Threshold'] = 0
    thresholds['Upper_Threshold'] = thresholds['mean'] + 3 * thresholds['std']
    df = df.merge(thresholds[['BA', 'Lower_Threshold', 'Upper_Threshold']], on='BA', how='left')

    # Read exception lookup table for BAs
    df_exception = pd.read_csv('ba_no_forec_lkup_table.csv')
    exception_BAs = set(df_exception['BA'])

    # Check for valid demand
    valid_demand_mask = (df['Demand'] >= df['Lower_Threshold']) & (df['Demand'] <= df['Upper_Threshold'])
    df['valid_demand'] = np.where(valid_demand_mask, df['Demand'], np.nan)

    # Impute demand
    forecast_mask = ~df['BA'].isin(exception_BAs) & pd.notna(df['demand_forecast'])
    df['imputed_demand'] = np.where(pd.isna(df['valid_demand']) & forecast_mask, df['demand_forecast'], df['valid_demand'])

    # Group by BA and perform fillna
    for _, group in df.groupby('BA'):
        group_index = group.index
        df.loc[group_index, 'imputed_demand'] = group['imputed_demand'].fillna(method='ffill', limit=1)
        df.loc[group_index, 'imputed_demand'] = group['imputed_demand'].fillna(group['imputed_demand'].shift(24))

    # Fill remaining NaNs with 0
    df['imputed_demand'].fillna(0, inplace=True)

    return df

# Apply the function
df_imp = fill_demand_ba(df_out)
