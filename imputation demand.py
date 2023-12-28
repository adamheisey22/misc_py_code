# Create dictionaries to store prior hour and prior day demand values for each BA
    prior_hour_demand_dict = {}
    prior_day_demand_dict = {}
    
    # Step 1: Check if a valid demand forecast value has been reported
    forecast_mask = (pd.notna(df['forecast'])) & (~df['no_forecast'])
    df['imputed_demand'] = np.where(forecast_mask, df['forecast'], np.nan)
    
    # Step 2: Check the prior hour for a valid demand value
    prior_hour_mask = df['imputed_demand'].isna() & (pd.notna(df['demand'].shift(1)))
    df.loc[prior_hour_mask, 'imputed_demand'] = df.loc[prior_hour_mask, 'demand'].shift(1)
    
    # Step 3: Check the corresponding hour from the prior day for a valid demand value
    prior_day_mask = df['imputed_demand'].isna() & (pd.notna(df['demand'].shift(24)))
    df.loc[prior_day_mask, 'imputed_demand'] = df.loc[prior_day_mask, 'demand'].shift(24)
    
    # Check for out-of-range values
    df['final_demand'] = np.clip(df['imputed_demand'], df['lower_threshold'], df['upper_threshold'])
    
    return df
