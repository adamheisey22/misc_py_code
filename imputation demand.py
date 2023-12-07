import pandas as pd

def impute_demand(df, forecast_exception_bas=None, demand_range_lookup=None):
    # Sort the DataFrame by timestamp if it's not already sorted
    df = df.sort_values(by='timestamp')

    # Create a dictionary to store imputed values
    imputed_values = {}

    # Iterate through each row in the DataFrame
    for index, row in df.iterrows():
        # Check if demand data is missing
        if pd.isna(row['demand']):
            # Check if a valid demand forecast value is available
            if pd.notna(row['demand_forecast']) and row['ba'] not in forecast_exception_bas:
                imputed_values[index] = row['demand_forecast']
            else:
                # Check the prior hour for a valid demand value
                prior_hour = df.iloc[index - 1] if index - 1 >= 0 else None
                if prior_hour is not None and pd.notna(prior_hour['demand']):
                    imputed_values[index] = prior_hour['demand']
                else:
                    # Check the corresponding hour from the prior day
                    prior_day = df[df['timestamp'] == row['timestamp'] - pd.Timedelta(days=1)]
                    if not prior_day.empty and pd.notna(prior_day.iloc[0]['demand']):
                        imputed_values[index] = prior_day.iloc[0]['demand']
                    else:
                        # If all steps fail, set the imputed value to 0
                        imputed_values[index] = 0
        else:
            # Check if the reported demand is out of a reasonable range
            if demand_range_lookup is not None:
                min_demand, max_demand = demand_range_lookup.get(row['ba'], (None, None))
                if min_demand is not None and max_demand is not None:
                    if row['demand'] < min_demand or row['demand'] > max_demand:
                        # Follow the same imputation steps as before
                        if pd.notna(row['demand_forecast']) and row['ba'] not in forecast_exception_bas:
                            imputed_values[index] = row['demand_forecast']
                        else:
                            prior_hour = df.iloc[index - 1] if index - 1 >= 0 else None
                            if prior_hour is not None and pd.notna(prior_hour['demand']):
                                imputed_values[index] = prior_hour['demand']
                            else:
                                prior_day = df[df['timestamp'] == row['timestamp'] - pd.Timedelta(days=1)]
                                if not prior_day.empty and pd.notna(prior_day.iloc[0]['demand']):
                                    imputed_values[index] = prior_day.iloc[0]['demand']
                                else:
                                    imputed_values[index] = 0

    # Update the DataFrame with imputed values
    df['imputed_demand'] = df.index.map(imputed_values)

    return df

# Example usage:
# df = impute_demand(df, forecast_exception_bas=['BA1', 'BA2'], demand_range_lookup={'BA1': (100, 500), 'BA2': (200, 600)})


#optimized code:
import pandas as pd

def impute_demand_optimized(df, forecast_exception_bas=None, demand_range_lookup=None):
    # Sort the DataFrame by timestamp if it's not already sorted
    df = df.sort_values(by='timestamp')

    # Create masks for missing demand and out-of-range demand
    missing_demand_mask = pd.isna(df['demand'])
    out_of_range_mask = (demand_range_lookup is not None) & ~missing_demand_mask

    # Check if a valid demand forecast value is available for missing demand
    forecast_mask = (
        missing_demand_mask &
        pd.notna(df['demand_forecast']) &
        ~df['ba'].isin(forecast_exception_bas)
    )

    # Check the prior hour for a valid demand value
    prior_hour_mask = (
        missing_demand_mask &
        ~forecast_mask &
        pd.notna(df['demand'].shift(1))
    )

    # Check the corresponding hour from the prior day
    prior_day_mask = (
        missing_demand_mask &
        ~forecast_mask &
        ~prior_hour_mask &
        df['timestamp'].sub(pd.DateOffset(days=1)).isin(df.loc[prior_hour_mask, 'timestamp'])
    )

    # Set imputed values based on the conditions
    df.loc[forecast_mask, 'imputed_demand'] = df.loc[forecast_mask, 'demand_forecast']
    df.loc[prior_hour_mask, 'imputed_demand'] = df.loc[prior_hour_mask, 'demand'].shift(1)
    df.loc[prior_day_mask, 'imputed_demand'] = df.loc[prior_day_mask, 'demand'].shift(24)
    df.loc[missing_demand_mask & ~(forecast_mask | prior_hour_mask | prior_day_mask), 'imputed_demand'] = 0

    # Check if the reported demand is out of a reasonable range
    if out_of_range_mask.any():
        for ba, (min_demand, max_demand) in demand_range_lookup.items():
            mask = (df['ba'] == ba) & out_of_range_mask & ((df['demand'] < min_demand) | (df['demand'] > max_demand))
            df.loc[mask, 'imputed_demand'] = df.loc[mask, 'imputed_demand'].fillna(0)

    return df

# Example usage:
# df = impute_demand_optimized(df, forecast_exception_bas=['BA1', 'BA2'], demand_range_lookup={'BA1': (100, 500), 'BA2': (200, 600)})
