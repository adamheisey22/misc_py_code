def extract_responses_to_dataframe(feedback_dict):
    """
    Converts the extracted feedback dictionary into a DataFrame but only includes the responses.
    """
    # Convert dictionary to DataFrame with only the responses
    df = pd.DataFrame(feedback_dict.values(), columns=['Response'])
    return df

# Convert the extracted feedback into a DataFrame with only the responses
responses_df = extract_responses_to_dataframe(feedback_extracted)

# Display the DataFrame to the user
tools.display_dataframe_to_user(name="Extracted Responses", dataframe=responses_df)
