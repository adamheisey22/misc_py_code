import pandas as pd
import numpy as np

def fill_demand_ba(df, df_threshold):
    # Convert relevant columns to numeric
    cols_to_convert = ['Demand', 'demand_forecast']
    df[cols_to_convert] = df[cols_to_convert].apply(pd.to_numeric, errors='coerce')

    # Convert 'Date' to datetime format and sort
    df['Date'] = pd.to_datetime(df['Date'])
    df.sort_values(by=['BA', 'Date', 'Hour'], inplace=True)

    # Merge predefined thresholds
    df = df.merge(df_threshold[['BA', 'Lower_Threshold', 'Upper_Threshold']], on='BA', how='left')

    # Calculate thresholds using 3 standard deviations for BAs without predefined thresholds
    thresholds = df.groupby('BA')['Demand'].agg(['mean', 'std']).reset_index()
    thresholds['Calculated_Upper_Threshold'] = thresholds['mean'] + 3 * thresholds['std']

    df = df.merge(thresholds[['BA', 'Calculated_Upper_Threshold']], on='BA', how='left')
    df['Upper_Threshold'].fillna(df['Calculated_Upper_Threshold'], inplace=True)
    df['Lower_Threshold'].fillna(0, inplace=True)  # Lower threshold set to 0

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

# Assuming df_threshold is the DataFrame with predefined thresholds
# Apply the function
df_imp = fill_demand_ba(df_out, df_threshold)
