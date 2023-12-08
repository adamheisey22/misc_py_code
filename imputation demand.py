import pandas as pd

def impute_demand(df):
    forecast_exception_list = set(['BA1', 'BA2', 'BA3'])  # Replace with your actual exception list
    valid_demand_range = {
        'BA1': (100, 500),
        'BA2': (200, 600),
        'BA3': (150, 450)
        # Add more BA entries as needed
    }  # Replace with your actual demand range lookup

    for index, row in df.iterrows():
        ba = row['BA']
        demand = row['demand']
        hour = row['hour']
        date = row['date']
        forecast_demand = row['forecast_demand']

        if pd.isnull(demand):
            imputed_demand = None

            # Rule 1: Use demand forecast value if available and not in the exception list
            if ba not in forecast_exception_list and pd.notnull(forecast_demand):
                imputed_demand = forecast_demand

            # Rule 2: Use prior hour's demand value if available
            elif hour > 0:
                prior_hour_demand = df.at[index - 1, 'demand']
                if pd.notnull(prior_hour_demand):
                    imputed_demand = prior_hour_demand

            # Rule 3: Use prior day's demand value for the corresponding hour if available
            elif date > df['date'].min():
                prior_day_demand = df[(df['BA'] == ba) & (df['date'] == date - pd.DateOffset(days=1)) & (df['hour'] == hour)]['demand'].values
                if len(prior_day_demand) > 0 and pd.notnull(prior_day_demand[0]):
                    imputed_demand = prior_day_demand[0]

            if imputed_demand is not None:
                df.at[index, 'demand'] = imputed_demand
            else:
                df.at[index, 'demand'] = 0  # Rule 4: No imputation is performed

        elif demand < valid_demand_range[ba][0] or demand > valid_demand_range[ba][1]:
            # Rule for imputing demand values outside the reasonable range
            imputed_demand = None

            # Rule 1: Use demand forecast value if available and not in the exception list
            if ba not in forecast_exception_list and pd.notnull(forecast_demand):
                imputed_demand = forecast_demand

            # Rule 2: Use prior hour's demand value if available
            elif hour > 0:
                prior_hour_demand = df.at[index - 1, 'demand']
                if pd.notnull(prior_hour_demand):
                    imputed_demand = prior_hour_demand

            # Rule 3: Use prior day's demand value for the corresponding hour if available
            elif date > df['date'].min():
                prior_day_demand = df[(df['BA'] == ba) & (df['date'] == date - pd.DateOffset(days=1)) & (df['hour'] == hour)]['demand'].values
                if len(prior_day_demand) > 0 and pd.notnull(prior_day_demand[0]):
                    imputed_demand = prior_day_demand[0]

            if imputed_demand is not None:
                df.at[index, 'demand'] = imputed_demand
            else:
                df.at[index, 'demand'] = 0  # Rule 3 failed, impute a value of 0

# Example usage:
# impute_demand(df)
