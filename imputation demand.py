import pandas as pd

def impute_demand_optimized(df, exception_list, threshold_limits):
    # Merge DataFrame with exception list
    df = pd.merge(df, exception_list, on='BA', how='left')

    # Step 1: Check for valid demand forecast value
    mask_step1 = (df['Forecast'].notnull()) & (df['Exception'].isnull())
    df.loc[mask_step1, 'ImputedDemand'] = df.loc[mask_step1, 'Forecast']

    # Step 2: Check for prior hour's demand value
    mask_step2 = (df['ImputedDemand'].isnull()) & (df['Demand'].shift(1).notnull())
    df.loc[mask_step2, 'ImputedDemand'] = df.loc[mask_step2, 'Demand'].shift(1)

    # Step 3: Check for prior day's demand value
    mask_step3 = (df['ImputedDemand'].isnull()) & (df['Demand'].shift(24).notnull())
    df.loc[mask_step3, 'ImputedDemand'] = df.loc[mask_step3, 'Demand'].shift(24)

    # Impute a value of 0 for step 3 failure
    df['ImputedDemand'].fillna(0, inplace=True)

    # Check for reasonable range (threshold limits) using vectorized operations
    mask_threshold = (
        (df['ImputedDemand'] >= threshold_limits['lower_threshold']) &
        (df['ImputedDemand'] <= threshold_limits['upper_threshold'])
    )
    df.loc[~mask_threshold, 'ImputedDemand'] = 0

    # Keep only relevant columns in the final DataFrame
    result_df = df[['BA', 'Hour', 'Demand', 'ImputedDemand']].copy()

    return result_df

# Example usage:
# df_imputed = impute_demand_optimized(df, exception_list, threshold_limits)
