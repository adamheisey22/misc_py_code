import pandas as pd

def impute_demand(df, forecast_table, demand_range_table, exception_list):
    for ba in df['BA'].unique():
        ba_mask = df['BA'] == ba

        forecast_values = forecast_table.get(ba, {})
        demand_range = demand_range_table.get(ba, {'min': 0, 'max': float('inf')})

        # Rule 1: Use demand forecast value if valid and not in the exception list
        forecast_mask = ~df['Hour'].isin(forecast_values.keys()) | (df['BA'].isin(exception_list))
        df.loc[ba_mask & forecast_mask & df['Demand'].isna(), 'Demand'] = df['Hour'].map(forecast_values)

        # Rule 2: Use prior hour's demand value if valid
        df.loc[ba_mask & df['Demand'].isna(), 'Demand'] = df['Hour'].map(df[ba_mask & (df['Hour'] == df['Hour'] - 1)]['Demand'])

        # Rule 3: Use prior day's demand value for the corresponding hour if valid
        df.loc[ba_mask & df['Demand'].isna(), 'Demand'] = df['Hour'].map(df[ba_mask & (df['Hour'] == df['Hour'] - 24)]['Demand'])

        # Rule 3 failed, impute a value of 0
        df.loc[ba_mask & df['Demand'].isna(), 'Demand'] = 0

        # Check if demand data is reported but out of reasonable range
        range_mask = (df['Demand'] < demand_range['min']) | (df['Demand'] > demand_range['max'])

        # Rule 1: Use demand forecast value if valid and not in the exception list
        df.loc[ba_mask & range_mask & forecast_mask, 'Demand'] = df['Hour'].map(forecast_values)

        # Rule 2: Use prior hour's demand value if valid
        df.loc[ba_mask & range_mask, 'Demand'] = df['Hour'].map(df[ba_mask & (df['Hour'] == df['Hour'] - 1)]['Demand'])

        # Rule 3: Use prior day's demand value for the corresponding hour if valid
        df.loc[ba_mask & range_mask, 'Demand'] = df['Hour'].map(df[ba_mask & (df['Hour'] == df['Hour'] - 24)]['Demand'])

        # Rule 3 failed, impute a value of 0
        df.loc[ba_mask & range_mask, 'Demand'] = 0

    return df

# Example usage:
# df = impute_demand(df, forecast_table, demand_range_table, exception_list)
