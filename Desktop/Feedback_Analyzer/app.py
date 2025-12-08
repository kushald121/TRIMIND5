import streamlit as st
import pandas as pd
import requests
from io import BytesIO

# flask --app api.py run --port=5000
prediction_endpoint = "http://127.0.0.1:5000/predict"

st.title("Text Sentiment Predictor")

uploaded_file = st.file_uploader(
    "Choose a CSV file for bulk prediction - Upload the file and click on Predict",
    type="csv",
)

# Text input for sentiment prediction
user_input = st.text_input("Enter text and click on Predict", "")

# Prediction on single sentence
if st.button("Predict"):
    if uploaded_file is not None:
        # Process CSV file
        file = {"file": uploaded_file}
        response = requests.post(prediction_endpoint, files=file)
        
        if response.status_code == 200:
            # Handle file download response
            response_bytes = BytesIO(response.content)
            
            st.download_button(
                label="Download Predictions",
                data=response_bytes,
                file_name="Predictions.csv",
                key="result_download_button",
            )
        else:
            st.error(f"API request failed with status code: {response.status_code}")
            try:
                error_response = response.json()
                st.error(f"Error: {error_response.get('error', 'Unknown error')}")
            except:
                st.error(f"Response content: {response.text}")
    else:
        # Process single text input
        if user_input.strip():
            response = requests.post(prediction_endpoint, json={"text": user_input})
            # Check if the response is successful and contains JSON
            if response.status_code == 200:
                try:
                    response_json = response.json()
                    if 'predicted_sentiment' in response_json:
                        st.write(f"Predicted sentiment: {response_json['predicted_sentiment']}")
                    elif 'error' in response_json:
                        st.error(f"Error: {response_json['error']}")
                    else:
                        st.error("Unexpected response format")
                except requests.exceptions.JSONDecodeError:
                    st.error(f"Failed to decode JSON response. Status code: {response.status_code}")
                    st.error(f"Response content: {response.text}")
            else:
                st.error(f"API request failed with status code: {response.status_code}")
                try:
                    error_response = response.json()
                    st.error(f"Error: {error_response.get('error', 'Unknown error')}")
                except:
                    st.error(f"Response content: {response.text}")
        else:
            st.warning("Please enter some text for prediction")