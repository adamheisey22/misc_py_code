import pandas as pd

def impute_demand(df, exception_list, demand_range_table):
    # Convert 'Date' to datetime format
    df['Date'] = pd.to_datetime(df['Date'])

    for ba in df['BA'].unique():
        ba_mask = df['BA'] == ba

        # Rule 1: Use demand forecast value if valid and not in the exception list
        forecast_mask = ~pd.isna(df['Forecast']) | df['BA'].isin(exception_list)
        df.loc[ba_mask & forecast_mask & pd.isna(df['Demand']), 'Demand'] = df['Forecast']

        # Rule 2: Use prior hour's demand value if valid
        prior_hour_mask = (df['Hour'] > 1) & pd.isna(df['Demand'])
        df.loc[ba_mask & prior_hour_mask, 'Demand'] = df['Hour'].map(df[ba_mask & (df['Hour'] == df['Hour'] - 1)]['Demand'])

        # Rule 3: Use corresponding hour from the prior day if valid
        prior_day_mask = (df['Hour'] == 1) & pd.isna(df['Demand'])
        df.loc[ba_mask & prior_day_mask, 'Demand'] = df['Hour'].map(df[ba_mask & (df['Hour'] == df['Hour'] - 24)]['Demand'])

        # Rule 3 failed, impute a value of 0
        df.loc[ba_mask & pd.isna(df['Demand']), 'Demand'] = 0

        # Check if demand data is reported but out of reasonable range
        if ba in demand_range_table:
            range_mask = (df['Demand'] < demand_range_table[ba]['min']) | (df['Demand'] > demand_range_table[ba]['max'])

            # Rule 1: Use demand forecast value if valid and not in the exception list
            df.loc[ba_mask & range_mask & forecast_mask, 'Demand'] = df['Forecast']

            # Rule 2: Use prior hour's demand value if valid
            df.loc[ba_mask & range_mask & prior_hour_mask, 'Demand'] = df['Hour'].map(df[ba_mask & (df['Hour'] == df['Hour'] - 1)]['Demand'])

            # Rule 3: Use corresponding hour from the prior day if valid
            df.loc[ba_mask & range_mask & prior_day_mask, 'Demand'] = df['Hour'].map(df[ba_mask & (df['Hour'] == df['Hour'] - 24)]['Demand'])

            # Rule 3 failed, impute a value of 0
            df.loc[ba_mask & range_mask, 'Demand'] = 0

    # Sort the DataFrame by 'Date' and 'Hour'
    df.sort_values(by=['Date', 'Hour'], inplace=True)

    return df

# Example usage:
# df = impute_demand(df, exception_list, demand_range_table)
