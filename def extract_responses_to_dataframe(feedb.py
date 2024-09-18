from docx import Document
import pandas as pd

def extract_feedback_from_multiple_docs(doc_paths):
    """
    Extracts all responses from multiple Word documents, after the questions, into a single DataFrame.
    """
    all_responses = []
    
    for doc_path in doc_paths:
        # Load each .docx file
        doc = Document(doc_path)
        
        current_question = None
        responses = []
        
        # Iterate over paragraphs to capture responses
        for para in doc.paragraphs:
            text = para.text.strip()
            if text.endswith('?'):  # If the paragraph ends with a question mark, it's a question
                current_question = text
            elif current_question and text:  # If it's not a question, it must be part of the response
                responses.append(text)
        
        all_responses.extend(responses)
    
    # Convert the combined responses into a DataFrame
    df = pd.DataFrame(all_responses, columns=['Response'])
    
    return df

# Example usage with multiple document paths
doc_paths = ['/path/to/file1.docx', '/path/to/file2.docx', '/path/to/file3.docx']  # Replace with actual file paths

# Extract feedback and display the combined DataFrame
combined_feedback_df = extract_feedback_from_multiple_docs(doc_paths)

# Display the DataFrame
import ace_tools as tools; tools.display_dataframe_to_user(name="Combined Feedback", dataframe=combined_feedback_df)
