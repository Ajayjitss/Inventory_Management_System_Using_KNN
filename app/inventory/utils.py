import joblib
import pandas as pd
import logging
from app import db
from .models import Inventory
from datetime import datetime
import pickle
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import os
from flask import current_app

# Set up logging
# logging.basicConfig(filename='inventory_predictions.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')



# Function to load the trained model from the pickle file
def load_model(model_path=None):
    if model_path is None:
        # Safe absolute path relative to your app folder
        model_path = os.path.join(current_app.root_path, 'inventory', 'knn_model.pkl')
    
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
        print("Model loaded successfully from:", model_path)
    return model
# Function to perform inference (predict sales for a given date and product)
def make_inference(target_date, target_product_id, model, sales_data_path=None):
    if sales_data_path is None:
        sales_data_path = os.path.join(current_app.root_path, 'inventory', 'Inventory_Sales_Data.csv')

    # Load the sales data for feature extraction
    new_sales_data = pd.read_csv(sales_data_path)

    # Convert Date into numeric feature (days since a reference date)
    new_sales_data['Date'] = pd.to_datetime(new_sales_data['Date'])
    new_sales_data['Date_numeric'] = (new_sales_data['Date'] - new_sales_data['Date'].min()).dt.days

    # Encode Product ID using LabelEncoder
    label_encoder = LabelEncoder()
    new_sales_data['Product_ID_encoded'] = label_encoder.fit_transform(new_sales_data['Product_ID'])

    # Prepare the input features for the prediction
    target_date_numeric = (target_date - new_sales_data['Date'].min()).days
    target_product_id_encoded = label_encoder.transform([target_product_id])[0]

    # Prepare the feature matrix
    X_inference = [[target_date_numeric, target_product_id_encoded]]

    # Make predictions
    predicted_sales = model.predict(X_inference)
    print(f"Predicted Sales for Product ID {target_product_id} on {target_date}: {predicted_sales[0]}")
    return predicted_sales[0]


# Step 1: Get all inventory items from the database
def update_inventory_predictions():
    # Get the current day (you can replace this with your logic to get the current day)
    target_date = pd.to_datetime(datetime.today().date()) 
    # Get the current date and time for the `last_checked_at` field
    current_datetime = datetime.now()
    # Step 2: Loop through each inventory item
    inventory_items = Inventory.query.all()
    model = load_model()

    for item in inventory_items:
        product_id = item.id
        
        # Step 3: Get product_id and use the inference function to predict the sales
        try:
            predicted_sales = make_inference(target_date,product_id, model)
            
            # Log predicted sales before updating
            print(f"Product ID: {product_id}, Predicted Sales: {predicted_sales}")
            
            # Step 4: Update the minimum_stock_required field with the predicted sales
            item.minimum_stock_required = predicted_sales
            item.last_checked_at = current_datetime
            # Log the update
            print(f"Updated Product ID: {product_id} with Predicted Sales: {predicted_sales}")
        
        except Exception as e:
            print(f"Error processing Product ID {product_id}: {str(e)}")
    
    # Step 5: Commit the changes to the database
    try:
        db.session.commit()
        print("Successfully updated all inventory items with predicted sales.")
    except Exception as e:
        print(f"Error committing changes to the database: {str(e)}")


# Run the update
# Uncomment this line to run the update when needed
# update_inventory_predictions()
