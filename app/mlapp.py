from flask import Flask, request, jsonify, render_template_string
import numpy as np
import pickle
import os
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

app = Flask(__name__)

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Iris Flower Predictor</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
        h1 { color: #333; }
        .form-group { margin: 15px 0; }
        label { display: inline-block; width: 200px; }
        input { padding: 5px; width: 150px; }
        button { background: #4CAF50; color: white; padding: 10px 20px; border: none; cursor: pointer; margin-top: 10px; }
        button:hover { background: #45a049; }
        .result { margin-top: 20px; padding: 15px; background: #f0f0f0; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>🌸 Iris Flower Predictor</h1>
    <p>Enter the flower measurements to predict its species:</p>
    
    <form id="predictionForm">
        <div class="form-group">
            <label>Sepal Length (cm):</label>
            <input type="number" step="0.1" name="sepal_length" required>
        </div>
        <div class="form-group">
            <label>Sepal Width (cm):</label>
            <input type="number" step="0.1" name="sepal_width" required>
        </div>
        <div class="form-group">
            <label>Petal Length (cm):</label>
            <input type="number" step="0.1" name="petal_length" required>
        </div>
        <div class="form-group">
            <label>Petal Width (cm):</label>
            <input type="number" step="0.1" name="petal_width" required>
        </div>
        <button type="submit">Predict Species</button>
    </form>
    
    <div id="result" class="result" style="display:none;">
        <h3>Prediction Result:</h3>
        <p id="species"></p>
        <p id="confidence"></p>
    </div>

    <script>
        document.getElementById('predictionForm').onsubmit = async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = {
                sepal_length: parseFloat(formData.get('sepal_length')),
                sepal_width: parseFloat(formData.get('sepal_width')),
                petal_length: parseFloat(formData.get('petal_length')),
                petal_width: parseFloat(formData.get('petal_width'))
            };
            
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            document.getElementById('species').textContent = 'Species: ' + result.species;
            document.getElementById('confidence').textContent = 'Confidence: ' + (result.confidence * 100).toFixed(2) + '%';
            document.getElementById('result').style.display = 'block';
        };
    </script>
</body>
</html>
"""

# Load or train model
MODEL_PATH = 'model.pkl'

def train_model():
    """Train a simple Random Forest model on Iris dataset"""
    iris = load_iris()
    X_train, X_test, y_train, y_test = train_test_split(
        iris.data, iris.target, test_size=0.2, random_state=42
    )
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump({'model': model, 'target_names': iris.target_names}, f)
    
    accuracy = model.score(X_test, y_test)
    print(f"Model trained with accuracy: {accuracy:.2f}")
    return model, iris.target_names

# Initialize model
if os.path.exists(MODEL_PATH):
    with open(MODEL_PATH, 'rb') as f:
        model_data = pickle.load(f)
        model = model_data['model']
        target_names = model_data['target_names']
else:
    model, target_names = train_model()

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        
        features = np.array([[
            data['sepal_length'],
            data['sepal_width'],
            data['petal_length'],
            data['petal_width']
        ]])
        
        prediction = model.predict(features)[0]
        probabilities = model.predict_proba(features)[0]
        confidence = float(np.max(probabilities))
        
        return jsonify({
            'species': target_names[prediction],
            'confidence': confidence,
            'all_probabilities': {
                name: float(prob) 
                for name, prob in zip(target_names, probabilities)
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)