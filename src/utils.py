import csv
import os
import time

import pandas as pd
import streamlit as st
import vertexai
from vertexai.generative_models import (
        Part
)

def extract_csv_content(pathname: str) -> list[Part]:
    """
    Extracts the content of a CSV file and returns it as a list of strings.

    Args:
        pathname (str): The path to the CSV file.

    Returns:
        list[str]: A list containing the content of the CSV file, with start and end indicators.
    """
    parts = [Part.from_text(f"--- START OF CSV {pathname} ---")]
    with open(pathname, "r", newline="") as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            parts.append(Part.from_text(" ".join(row)))
    parts.append(Part.from_text(f"--- END OF CSV {pathname} ---"))
    return parts


def save_uploaded_file(uploaded_file, save_directory):
    """
    Saves the uploaded file to the specified directory.

    Args:
        uploaded_file (streamlit.uploadedfile.UploadedFile): The uploaded file.
        save_directory (str): The directory where the file will be saved.

    Returns:
        str: The path where the file is saved.
    """
    file_name = "file.csv"  # You might want to customize the file name
    file_path = os.path.join(save_directory, file_name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    saved_file_path = os.path.join(save_directory, file_name)
    success_message = st.success("File saved successfully!")
    time.sleep(1)  # Wait for 1 second (change if needed)
    success_message.empty()  # Empty the success message

    # Create a DataFrame from the saved CSV file
    df = pd.read_csv(file_path, sep = ',')
    df['play_id'] = df['play_id'].astype(str)
    # Display the first few rows of the DataFrame
    st.write("Preview of the DataFrame:")
    st.write(df.head(n=1))

    return saved_file_path
