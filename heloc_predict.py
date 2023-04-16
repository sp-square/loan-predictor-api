from flask import Flask, jsonify, request
from flask_cors import CORS
import joblib
import pandas as pd
import os

app = Flask(__name__)
CORS(app)


@app.route("/")
def index():
    # return content and a response code
    return "<h1>Welcome to my App</h1>", 200


@app.route('/predict')
def predict():
    # Parse out feature_data from input variables passed from the query string
    test_url = 'http://127.0.0.1:5000/predict?loan=1100&mortdue=25860.0&value=39025.0&yoj=10.5&derog=0.0&delinq=0.0&clage=94.366667&ninq=1.0&clno=9.0&debtinc=34.818262&reason=HomeImp&job=Other'
    feature_data = extract_feature_data(request.args)
    # Convert json to pandas df (matching column names)
    df = pd.DataFrame(feature_data)
    df = df.reindex(columns=col_names)

    # Predict
    try:
        prediction = model.predict(df)
    except:
        prediction = None

    # Return the prediction as a json response
    if prediction is not None:
        return jsonify({'prediction': str(prediction)}), 200
    else:
        return jsonify({'error': 'Oops! Something went wrong!'}), 400


def extract_feature_data(query_args):
    features = {
        'LOAN': query_args.get('loan', ''),
        'MORTDUE': query_args.get('mortdue', ''),
        'VALUE': query_args.get('value', ''),
        'YOJ': query_args.get('yoj', ''),
        'DEROG': query_args.get('derog', ''),
        'DELINQ': query_args.get('delinq', ''),
        'CLAGE': query_args.get('clage', ''),
        'NINQ': query_args.get('ninq', ''),
        'CLNO': query_args.get('clno', ''),
        'DEBTINC': query_args.get('debtinc', '')
    }

    # Format 'REASON_'
    reason = query_args.get('reason', '')
    if reason == 'HomeImp':
        features['REASON_HomeImp'] = 1
    else:
        features['REASON_HomeImp'] = 0
    # Format 'JOB_'
    job = query_args.get('job', '')
    if job == 'Office':
        features['JOB_Office'] = 1
        features['JOB_Other'] = 0
        features['JOB_ProfExe'] = 0
        features['JOB_Sales'] = 0
        features['JOB_Self'] = 0
    elif job == 'Other':
        features['JOB_Office'] = 0
        features['JOB_Other'] = 1
        features['JOB_ProfExe'] = 0
        features['JOB_Sales'] = 0
        features['JOB_Self'] = 0
    elif job == 'ProfExe':
        features['JOB_Office'] = 0
        features['JOB_Other'] = 0
        features['JOB_ProfExe'] = 1
        features['JOB_Sales'] = 0
        features['JOB_Self'] = 0
    elif job == 'Sales':
        features['JOB_Office'] = 0
        features['JOB_Other'] = 0
        features['JOB_ProfExe'] = 0
        features['JOB_Sales'] = 1
        features['JOB_Self'] = 0
    elif job == 'Self':
        features['JOB_Office'] = 0
        features['JOB_Other'] = 0
        features['JOB_ProfExe'] = 0
        features['JOB_Sales'] = 0
        features['JOB_Self'] = 1
    else:
        features['JOB_Office'] = 0
        features['JOB_Other'] = 0
        features['JOB_ProfExe'] = 0
        features['JOB_Sales'] = 0
        features['JOB_Self'] = 0
    return [features]


if __name__ == "__main__":
    model = joblib.load('loan_default_final_model.pkl')
    col_names = joblib.load('loan_default_col_names.pkl')
    # Heroku will set the PORT environment variable for web traffic
    port = os.environ.get('PORT', 5000)
    # set debug=False before deployment
    app.run(debug=False, host='0.0.0.0', port=port)
