import os
from docx import Document
import pandas as pd

def extract_feedback_from_folder(folder_path):
    """
    Extracts all responses from multiple .docx files in a folder, after the questions,
    into a single DataFrame, and tags each response with the file name's 'name' part.
    Assumes file names follow the format: 'form_g1_name.docx'
    """
    all_responses = []
    
    # Iterate over all files in the folder
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".docx"):
            # Extract the 'name' part from the file name (e.g., 'form_g1_heisey.docx' -> 'heisey')
            name_tag = file_name.split('_')[-1].replace('.docx', '')
            
            # Load the document
            doc_path = os.path.join(folder_path, file_name)
            doc = Document(doc_path)
            
            current_question = None
            responses = []
            
            # Iterate over paragraphs to capture responses
            for para in doc.paragraphs:
                text = para.text.strip()
                if text.endswith('?'):  # If the paragraph ends with a question mark, it's a question
                    current_question = text
                elif current_question and text:  # If it's not a question, it must be part of the response
                    responses.append({'Response': text, 'Name': name_tag})
            
            all_responses.extend(responses)
    
    # Convert the combined responses into a DataFrame
    df = pd.DataFrame(all_responses)
    
    return df

# Example usage with a folder path
folder_path = '/path/to/your/folder'  # Replace with actual folder path containing .docx files

# Extract feedback and save the DataFrame
combined_feedback_df = extract_feedback_from_folder(folder_path)

# Save the DataFrame to a CSV file
combined_feedback_df.to_csv("combined_feedback.csv", index=False)
