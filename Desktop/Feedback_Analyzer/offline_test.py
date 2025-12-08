import pandas as pd
import pickle
import re
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import numpy as np

# Load models
STOPWORDS = set(stopwords.words("english"))
predictor = pickle.load(open(r"model/model_xgb.pkl", "rb"))
scaler = None
try:
    scaler = pickle.load(open(r"model/scaler.pkl", "rb"))
except Exception:
    scaler = None
cv = pickle.load(open(r"model/countVectorizer.pkl", "rb"))

# Read test data
data = pd.read_csv('sample_data.csv')
print(f"Data shape: {data.shape}")
print(f"Columns: {data.columns.tolist()}")
print(f"Data:\n{data}")

# Process data
corpus = []
stemmer = PorterStemmer()
for i in range(0, data.shape[0]):
    print(f"Processing row {i}: {data.iloc[i]['Sentence']}")
    review = re.sub("[^a-zA-Z]", " ", str(data.iloc[i]["Sentence"]))
    review = review.lower().split()
    review = [stemmer.stem(word) for word in review if not word in STOPWORDS]
    review = " ".join(review)
    corpus.append(review)

print(f"Corpus: {corpus}")

# Transform and predict
X_prediction = cv.transform(corpus).toarray()
print(f"Transformed data shape: {X_prediction.shape}")
if scaler is not None:
    X_prediction = scaler.transform(X_prediction)

if hasattr(predictor, "predict_proba"):
    y_probs = predictor.predict_proba(X_prediction)
    print(f"Prediction probabilities: {y_probs}")
    
    # Apply threshold logic
    y_predictions = []
    for i in range(len(y_probs)):
        prob_class_0 = y_probs[i][0]  # Probability of class 0 (assumed Negative)
        prob_class_1 = y_probs[i][1]  # Probability of class 1 (assumed Positive)
        print(f"Row {i}: Probabilities [Negative: {prob_class_0:.4f}, Positive: {prob_class_1:.4f}]")
        
        # Workaround for model issue: Use a stricter threshold
        if prob_class_1 > 0.9:  # Very high confidence for Positive
            y_predictions.append("Positive")
        elif prob_class_0 > 0.7:  # Higher confidence for Negative
            y_predictions.append("Negative")
        else:
            # Default to Negative for ambiguous cases
            y_predictions.append("Negative")
    
    print(f"Final predictions: {y_predictions}")
    data["Predicted sentiment"] = y_predictions
    
    # Save results
    data.to_csv('offline_predictions.csv', index=False)
    print("Predictions saved to offline_predictions.csv")
else:
    print("Model does not support predict_proba")