# Import necessary libraries
import numpy as np
import joblib  # For loading the serialized model
import pandas as pd  # For data manipulation
from flask import Flask, request, jsonify  # For creating the Flask API

# Initialize the Flask application
superkart_sales_predictor_api = Flask("SuperKart Sales Predictor")

# Load the trained machine learning pipeline (preprocessing + model)
model = joblib.load("superkart_sales_prediction_model_v1_0.joblib")


@superkart_sales_predictor_api.get('/')
def home():
    """Health-check / welcome message for the API root."""
    return "Welcome to the SuperKart Sales Prediction API!"


@superkart_sales_predictor_api.post('/v1/sales')
def predict_sales():
    """
    Single (online) prediction.
    Expects a JSON payload with the product/store features and returns the
    predicted total sales as a JSON response.
    """
    product_data = request.get_json()

    # Assemble the feature dictionary expected by the pipeline
    sample = {
        'Product_Weight': product_data['Product_Weight'],
        'Product_Sugar_Content': product_data['Product_Sugar_Content'],
        'Product_Allocated_Area': product_data['Product_Allocated_Area'],
        'Product_MRP': product_data['Product_MRP'],
        'Store_Size': product_data['Store_Size'],
        'Store_Location_City_Type': product_data['Store_Location_City_Type'],
        'Store_Type': product_data['Store_Type'],
        'Product_Id_char': product_data['Product_Id_char'],
        'Store_Age_Years': product_data['Store_Age_Years'],
        'Product_Type_Category': product_data['Product_Type_Category'],
    }

    input_data = pd.DataFrame([sample])

    # Predict and convert to a native Python float for JSON serialization
    prediction = round(float(model.predict(input_data)[0]), 2)

    return jsonify({'Predicted Product Store Sales Total': prediction})


@superkart_sales_predictor_api.post('/v1/salesbatch')
def predict_sales_batch():
    """
    Batch prediction.
    Expects a CSV file (multipart/form-data, field name 'file') whose columns
    match the model's feature set, and returns a prediction for every row.
    """
    file = request.files['file']
    input_data = pd.read_csv(file)

    # Drop any fully empty rows that may come from trailing newlines
    input_data = input_data.dropna(how="all")

    predictions = [round(float(p), 2) for p in model.predict(input_data)]

    # Key each prediction by its row index
    output_dict = {int(i): pred for i, pred in enumerate(predictions)}
    return jsonify(output_dict)


if __name__ == '__main__':
    superkart_sales_predictor_api.run(debug=True)
