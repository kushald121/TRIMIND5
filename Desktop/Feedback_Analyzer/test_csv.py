import requests

# Test CSV file upload
with open('sample_data.csv', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://127.0.0.1:5000/predict', files=files)
    print(f"Status code: {response.status_code}")
    print(f"Response headers: {response.headers}")
    print(f"Response content: {response.text[:500]}")
    
    # Save the response to a file if it's successful
    if response.status_code == 200:
        with open('test_predictions.csv', 'wb') as out_f:
            out_f.write(response.content)
        print("Predictions saved to test_predictions.csv")