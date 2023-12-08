import pandas as pd

def impute_demand(df):
    forecast_exception_list = set(['BA1', 'AVA', 'BA3'])  # Replace with your actual exception list
    valid_demand_range = {
        'BA1': (100, 500),
        # 'AVA': No valid demand range specified,
        'BA3': (150, 450)
        # Add more BA entries as needed
    }  # Replace with your actual demand range lookup

    for index, row in df.iterrows():
        ba = row['BA']  # Assuming 'BA' is the column name for the BA identifier
        demand = row['demand']  # Assuming 'demand' is the column name for the demand values
        hour = row['hour']  # Assuming 'hour' is the column name for the hour values
        date = row['date']  # Assuming 'date' is the column name for the date values
        forecast_demand = row['forecast_demand']  # Assuming 'forecast_demand' is the column name for forecast values

        # Rule for imputing missing demand values
        if pd.isnull(demand):
            # Rule 1: Use demand forecast value if available and not in the exception list
            if ba not in forecast_exception_list and pd.notnull(forecast_demand):
                df.at[index, 'demand'] = forecast_demand
            else:
                # Rule 2: Use prior hour's demand value if available
                prior_hour_demand = df[(df['BA'] == ba) & (df['hour'] == hour - 1)]['demand'].values
                if len(prior_hour_demand) > 0 and pd.notnull(prior_hour_demand[0]):
                    df.at[index, 'demand'] = prior_hour_demand[0]
                else:
                    # Rule 3: Use prior day's demand value for the corresponding hour if available
                    prior_day_demand = df[(df['BA'] == ba) & (df['date'] == date - pd.DateOffset(days=1)) & (df['hour'] == hour)]['demand'].values
                    if len(prior_day_demand) > 0 and pd.notnull(prior_day_demand[0]):
                        df.at[index, 'demand'] = prior_day_demand[0]
                    else:
                        # Rule 4: No imputation is performed
                        pass
        else:
            # Rule for imputing demand values outside the reasonable range
            if ba in valid_demand_range and (demand < valid_demand_range[ba][0] or demand > valid_demand_range[ba][1]):
                # Rule 1: Use demand forecast value if available and not in the exception list
                if ba not in forecast_exception_list and pd.notnull(forecast_demand):
                    df.at[index, 'demand'] = forecast_demand
                else:
                    # Rule 2: Use prior hour's demand value if available
                    prior_hour_demand = df[(df['BA'] == ba) & (df['hour'] == hour - 1)]['demand'].values
                    if len(prior_hour_demand) > 0 and pd.notnull(prior_hour_demand[0]):
                        df.at[index, 'demand'] = prior_hour_demand[0]
                    else:
                        # Rule 3: Use prior day's demand value for the corresponding hour if available
                        prior_day_demand = df[(df['BA'] == ba) & (df['date'] == date - pd.DateOffset(days=1)) & (df['hour'] == hour)]['demand'].values
                        if len(prior_day_demand) > 0 and pd.notnull(prior_day_demand[0]):
                            df.at[index, 'demand'] = prior_day_demand[0]
                        else:
                            # Rule 3 failed, impute a value of 0
                            df.at[index, 'demand'] = 0

# Example usage:
# impute_demand(df)
