import os
import pandas as pd
import requests
import streamlit as st

# Base URL of the deployed Flask backend Space (public URL).
# Set the BACKEND_URL environment variable / Space secret, or edit the default below.
# Inside the Codespace, the backend container is reachable by its name on the
# shared Docker network. Override with the BACKEND_URL env var if needed.
BACKEND_URL = os.environ.get("BACKEND_URL", "http://backend:7860")

st.set_page_config(page_title="SuperKart Sales Prediction", page_icon="🛒")
st.title("🛒 SuperKart Sales Prediction")
st.write("Forecast the total sales revenue of a product in a given store.")

# ------------------------- Online (single) prediction -------------------------
st.subheader("Online Prediction")

col1, col2 = st.columns(2)
with col1:
    product_weight = st.number_input("Product Weight", min_value=0.0, value=12.66, step=0.1)
    product_allocated_area = st.number_input("Product Allocated Area (ratio)", min_value=0.0,
                                              max_value=1.0, value=0.03, step=0.001, format="%.3f")
    product_mrp = st.number_input("Product MRP", min_value=0.0, value=140.0, step=1.0)
    store_age_years = st.number_input("Store Age (years)", min_value=0, value=10, step=1)
    product_sugar_content = st.selectbox("Product Sugar Content",
                                         ["Low Sugar", "Regular", "No Sugar"])
with col2:
    store_size = st.selectbox("Store Size", ["Small", "Medium", "High"])
    store_location_city_type = st.selectbox("Store Location City Type",
                                             ["Tier 1", "Tier 2", "Tier 3"])
    store_type = st.selectbox("Store Type",
                              ["Supermarket Type1", "Supermarket Type2",
                               "Departmental Store", "Food Mart"])
    product_id_char = st.selectbox("Product Id Char (FD=Food, DR=Drinks, NC=Non-Consumable)",
                                   ["FD", "DR", "NC"])
    product_type_category = st.selectbox("Product Type Category",
                                         ["Perishables", "Non Perishables"])

payload = {
    "Product_Weight": product_weight,
    "Product_Sugar_Content": product_sugar_content,
    "Product_Allocated_Area": product_allocated_area,
    "Product_MRP": product_mrp,
    "Store_Size": store_size,
    "Store_Location_City_Type": store_location_city_type,
    "Store_Type": store_type,
    "Product_Id_char": product_id_char,
    "Store_Age_Years": store_age_years,
    "Product_Type_Category": product_type_category,
}

if st.button("Predict", type="primary"):
    try:
        response = requests.post(f"{BACKEND_URL}/v1/sales", json=payload, timeout=60)
        if response.status_code == 200:
            pred = response.json()["Predicted Product Store Sales Total"]
            st.success(f"Predicted Product Store Sales Total: ₹ {pred:,.2f}")
        else:
            st.error(f"API error: {response.status_code}")
    except Exception as e:
        st.error(f"Unable to connect to the prediction API: {e}")

# ------------------------------ Batch prediction ------------------------------
st.subheader("Batch Prediction")
uploaded_file = st.file_uploader("Upload a CSV file for batch prediction", type=["csv"])

if uploaded_file is not None and st.button("Predict Batch", type="primary"):
    try:
        response = requests.post(f"{BACKEND_URL}/v1/salesbatch",
                                 files={"file": uploaded_file}, timeout=120)
        if response.status_code == 200:
            preds = response.json()
            result = pd.DataFrame({
                "Row": list(preds.keys()),
                "Predicted_Sales": list(preds.values()),
            })
            st.success("Batch predictions completed!")
            st.dataframe(result)
        else:
            st.error(f"API error: {response.status_code}")
    except Exception as e:
        st.error(f"Unable to connect to the prediction API: {e}")
