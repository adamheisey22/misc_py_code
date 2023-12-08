import pandas as pd

def impute_demand(df, forecast_table, demand_range_table):
    for index, row in df.iterrows():
        ba = row['BA']  # Replace 'BA' with the actual column name for BA
        hour = row['Hour']  # Replace 'Hour' with the actual column name for Hour
        demand = row['Demand']  # Replace 'Demand' with the actual column name for Demand

        # Check if demand data is missing
        if pd.isna(demand):
            # Rule 1: Use demand forecast value if valid and not in the exception list
            forecast_value = forecast_table.get(ba, {}).get(hour)
            if forecast_value is not None and ba not in exception_list:
                df.at[index, 'Demand'] = forecast_value
            else:
                # Rule 2: Use prior hour's demand value if valid
                prior_hour_demand = df[(df['BA'] == ba) & (df['Hour'] == hour - 1)]['Demand'].values
                if len(prior_hour_demand) > 0 and not pd.isna(prior_hour_demand[0]):
                    df.at[index, 'Demand'] = prior_hour_demand[0]
                else:
                    # Rule 3: Use prior day's demand value for the corresponding hour if valid
                    prior_day_demand = df[(df['BA'] == ba) & (df['Hour'] == hour - 24)]['Demand'].values
                    if len(prior_day_demand) > 0 and not pd.isna(prior_day_demand[0]):
                        df.at[index, 'Demand'] = prior_day_demand[0]

        # Check if demand data is reported but out of reasonable range
        elif demand < demand_range_table.get(ba, {}).get('min', 0) or demand > demand_range_table.get(ba, {}).get('max', float('inf')):
            # Rule 1: Use demand forecast value if valid and not in the exception list
            forecast_value = forecast_table.get(ba, {}).get(hour)
            if forecast_value is not None and ba not in exception_list:
                df.at[index, 'Demand'] = forecast_value
            else:
                # Rule 2: Use prior hour's demand value if valid
                prior_hour_demand = df[(df['BA'] == ba) & (df['Hour'] == hour - 1)]['Demand'].values
                if len(prior_hour_demand) > 0 and not pd.isna(prior_hour_demand[0]):
                    df.at[index, 'Demand'] = prior_hour_demand[0]
                else:
                    # Rule 3: Use prior day's demand value for the corresponding hour if valid
                    prior_day_demand = df[(df['BA'] == ba) & (df['Hour'] == hour - 24)]['Demand'].values
                    if len(prior_day_demand) > 0 and not pd.isna(prior_day_demand[0]):
                        df.at[index, 'Demand'] = prior_day_demand[0]
                    else:
                        # Rule 3 failed, impute a value of 0
                        df.at[index, 'Demand'] = 0

    return df

# Replace the column names and exception list with your actual data
# Example usage:
# df = impute_demand(df, forecast_table, demand_range_table)
