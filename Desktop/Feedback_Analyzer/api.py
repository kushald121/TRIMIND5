from flask import Flask, request, jsonify, send_file, render_template
import re
from io import BytesIO

from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import matplotlib.pyplot as plt
import pandas as pd
import pickle
import base64

STOPWORDS = set(stopwords.words("english"))

app = Flask(__name__)

@app.route("/test", methods=["GET"])
def test():
    return "Test request received successfully. Service is running."

@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("landing.html")

@app.route("/analyze", methods=["GET"])
def analyze():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    try:
        predictor = pickle.load(open(r"model/model_xgb.pkl", "rb"))
        scaler = None
        try:
            scaler = pickle.load(open(r"model/scaler.pkl", "rb"))
        except Exception:
            scaler = None
        cv = pickle.load(open(r"model/countVectorizer.pkl", "rb"))
    except Exception as e:
        return jsonify({"error": f"Failed to load models: {str(e)}"}), 500

    try:
        ## Check if request contains a file or text input
        if "file" in request.files:
            file = request.files["file"]
            
            # Read file content into memory and create a new BytesIO object
            # This avoids issues with file pointer positions
            file_content = file.read()
            file_stream = BytesIO(file_content)
            
            try:
                data = pd.read_csv(file_stream)
            except Exception as e:
                return jsonify({"error": f"Failed to read CSV file: {str(e)}"}), 400

            predictions, graph = bulk_prediction(predictor, scaler, cv, data)

            response = send_file(
                predictions,
                mimetype="text/csv",
                as_attachment=True,
                download_name="Predictions.csv",
            )

            response.headers["X-Graph-Exists"] = "true"

            response.headers["X-Graph-Data"] = base64.b64encode(
                graph.getbuffer()
            ).decode("ascii")

            return response

        elif request.is_json and "text" in request.get_json():
            text_input = request.get_json()["text"]
            predicted_sentiment = single_prediction(predictor, scaler, cv, text_input)
            return jsonify({"predicted_sentiment": predicted_sentiment})
        
        elif "text" in request.form:
            text_input = request.form["text"]
            predicted_sentiment = single_prediction(predictor, scaler, cv, text_input)
            return jsonify({"predicted_sentiment": predicted_sentiment})

        else:
            return jsonify({"error": "Provide file upload (multipart/form-data) or JSON with 'text' key."}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def single_prediction(predictor, scaler, cv, text_input):
    try:
        corpus = []
        stemmer = PorterStemmer()
        review = re.sub("[^a-zA-Z]", " ", text_input)
        review = review.lower().split()
        review = [stemmer.stem(word) for word in review if not word in STOPWORDS]
        review = " ".join(review)
        corpus.append(review)

        X_prediction = cv.transform(corpus).toarray()
        if scaler is not None:
            X_prediction = scaler.transform(X_prediction)

        if hasattr(predictor, "predict_proba"):
            y_probs = predictor.predict_proba(X_prediction)
            # Get the class with highest probability
            y_pred_idx = y_probs.argmax(axis=1)[0]
            
            # Since we know the classes are [0, 1] where 0=Negative and 1=Positive
            # But the model might have been trained with opposite labels
            # Let's check the actual probabilities
            prob_class_0 = y_probs[0][0]  # Probability of class 0 (assumed Negative)
            prob_class_1 = y_probs[0][1]  # Probability of class 1 (assumed Positive)
            
            # Workaround for model issue: Use a stricter threshold
            # Only classify as Positive if the probability is significantly higher
            if prob_class_1 > 0.9:  # Very high confidence for Positive
                result = "Positive"
            elif prob_class_0 > 0.7:  # Higher confidence for Negative
                result = "Negative"
            else:
                # Default to Negative for ambiguous cases
                # This is a workaround for the poorly trained model
                result = "Negative"
        else:
            y_pred = predictor.predict(X_prediction)[0]
            # Convert to int to be safe
            y_pred_idx = int(y_pred)
            # Standard convention: 0=Negative, 1=Positive
            result = "Negative" if y_pred_idx == 0 else "Positive"

        return result
    except Exception as e:
        raise Exception(f"Error in single prediction: {str(e)}")


def bulk_prediction(predictor, scaler, cv, data):
    try:
        corpus = []
        stemmer = PorterStemmer()
        for i in range(0, data.shape[0]):
            review = re.sub("[^a-zA-Z]", " ", str(data.iloc[i]["Sentence"]))
            review = review.lower().split()
            review = [stemmer.stem(word) for word in review if not word in STOPWORDS]
            review = " ".join(review)
            corpus.append(review)

        X_prediction = cv.transform(corpus).toarray()
        if scaler is not None:
            X_prediction = scaler.transform(X_prediction)

        y_predictions = []
        if hasattr(predictor, "predict_proba"):
            y_probs = predictor.predict_proba(X_prediction)
            # Apply the same threshold logic as in single_prediction
            for i in range(len(y_probs)):
                prob_class_0 = y_probs[i][0]  # Probability of class 0 (assumed Negative)
                prob_class_1 = y_probs[i][1]  # Probability of class 1 (assumed Positive)
                
                # Workaround for model issue: Use a stricter threshold
                # Only classify as Positive if the probability is significantly higher
                if prob_class_1 > 0.9:  # Very high confidence for Positive
                    y_predictions.append("Positive")
                elif prob_class_0 > 0.7:  # Higher confidence for Negative
                    y_predictions.append("Negative")
                else:
                    # Default to Negative for ambiguous cases
                    # This is a workaround for the poorly trained model
                    y_predictions.append("Negative")
        else:
            y_preds = predictor.predict(X_prediction)
            # Apply standard mapping for direct predictions
            for y_pred in y_preds:
                y_pred_idx = int(y_pred)
                # Standard convention: 0=Negative, 1=Positive
                y_predictions.append("Negative" if y_pred_idx == 0 else "Positive")

        data["Predicted sentiment"] = y_predictions
        predictions_csv = BytesIO()

        data.to_csv(predictions_csv, index=False)
        predictions_csv.seek(0)

        graph = get_distribution_graph(data)

        return predictions_csv, graph
    except Exception as e:
        raise Exception(f"Error in bulk prediction: {str(e)}")


def get_distribution_graph(data):
    fig = plt.figure(figsize=(5, 5))
    colors = ("green", "red")
    wp = {"linewidth": 1, "edgecolor": "black"}
    tags = data["Predicted sentiment"].value_counts()
    explode = (0.01, 0.01)

    tags.plot(
        kind="pie",
        autopct="%1.1f%%",
        shadow=True,
        colors=colors,
        startangle=90,
        wedgeprops=wp,
        explode=explode,
        title="Sentiment Distribution",
        xlabel="",
        ylabel="",
    )

    graph = BytesIO()
    plt.savefig(graph, format="png")
    plt.close()
    graph.seek(0)

    return graph


if __name__ == "__main__":
    app.run(port=5000, debug=True)