import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString, Point
import random
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import sqlite3

# Set boundaries for the Save Conservancy
x_min, x_max = 31.794, 32.335
y_min, y_max = -20.918, -19.948

# Function to calculate Euclidean distance between two points
def calculate_distance(point1, point2):
    return np.linalg.norm(point1 - point2)

# Function to determine the season based on the month
def get_season(date):
    month = date.month
    if month in [12, 1, 2]:
        return "Winter"
    elif month in [3, 4, 5]:
        return "Spring"
    elif month in [6, 7, 8]:
        return "Summer"
    elif month in [9, 10, 11]:
        return "Autumn"
    else:
        return "Unknown"

# Function to aggregate features over time (RFA)
def aggregate_features(paths, window_size=5):
    """
    Aggregate features over time using a rolling window.
    """
    aggregated_features = []
    for path in paths:
        path_features = []
        for i in range(len(path) - window_size):
            window = path[i:i + window_size]
            # Aggregate features: mean and std of X and Y coordinates
            mean_x = np.mean([p[0] for p in window])
            mean_y = np.mean([p[1] for p in window])
            std_x = np.std([p[0] for p in window])
            std_y = np.std([p[1] for p in window])
            path_features.append([mean_x, mean_y, std_x, std_y])
        aggregated_features.append(path_features)
    return aggregated_features

# Function to train an ML model (Random Forest)
def train_ml_model(X=None, y=None):
    """
    Train a Random Forest model.
    If X and y are not provided, loads data from the database.
    """
    if X is None or y is None:
        # Connect to database and get data
        try:
            conn = sqlite3.connect('Quelea Birds database.db')
            df = pd.read_sql_query("SELECT * FROM migration_data", conn)
            
            # Simulate paths
            paths = simulate_migration(df, num_steps=100)
            
            # Prepare features
            window_size = 5
            aggregated_features = aggregate_features(paths, window_size=window_size)
            X = np.vstack([np.array(features).flatten() for features in aggregated_features])
            y = np.array([calculate_distance(path[0], path[-1]) for path in paths])
            
            conn.close()
        except Exception as e:
            print(f"Error preparing data for ML model: {e}")
            # Return a simple model if there's an error
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            return model
    
    # Train the model
    try:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        print(f"Model MSE: {mse}")
        return model
    except Exception as e:
        print(f"Error training ML model: {e}")
        # Return an untrained model as fallback
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        return model

# Function to simulate migration paths using parameters from the database
def simulate_migration(parameters_df, num_steps=100):
    """
    Simulate migration paths based on parameters from the database.
    """
    paths = []
    
    # Handle empty dataframe
    if parameters_df is None or len(parameters_df) == 0:
        # Create some dummy data for testing
        dummy_data = {
            'longitude': [32.0],
            'latitude': [-20.5],
            'drift_strength': [0.05],
            'noise_std': [0.01],
            'step_size': [0.01]
        }
        parameters_df = pd.DataFrame(dummy_data)
        
    for idx, row in parameters_df.iterrows():
        # Initialize starting position
        pos = np.array([row['longitude'], row['latitude']])
        path = [pos.copy()]

        # Drift and noise parameters
        drift_strength = row.get('drift_strength', 0.05)
        noise_std = row.get('noise_std', 0.01)
        step_size = row.get('step_size', 0.01)

        for t in range(num_steps):
            # Random drift direction
            drift_direction = np.random.uniform(-1, 1, 2)
            drift_direction /= np.linalg.norm(drift_direction)  # Normalize to unit vector

            # Apply drift and noise
            drift = drift_strength * drift_direction
            noise = np.random.normal(0, noise_std, 2)
            pos = pos + drift + noise

            # Enforce boundaries
            pos[0] = np.clip(pos[0], x_min, x_max)
            pos[1] = np.clip(pos[1], y_min, y_max)

            # Append new position to the path
            path.append(pos.copy())

        paths.append(path)
    return paths

# Function to generate random colors
def generate_random_color():
    return f"#{random.randint(0, 0xFFFFFF):06x}"

# Function to create migration map data 
def generate_migration_map_data(parameters_df=None):
    """
    Generate migration paths and prepare map data.
    If parameters_df is not provided, load from database.
    """
    try:
        # If no parameters provided, load from database
        if parameters_df is None:
            conn = sqlite3.connect('Quelea Birds database.db')
            parameters_df = pd.read_sql_query("SELECT * FROM migration_data", conn)
            conn.close()
        
        # Simulate migration paths
        paths = simulate_migration(parameters_df, num_steps=100)
        
        # Create map data
        map_data = []
        for idx, path in enumerate(paths):
            color = generate_random_color()
            path_coords = [(point[1], point[0]) for point in path]  # Folium expects (lat, lng)
            
            map_data.append({
                'id': idx + 1,
                'color': color,
                'path': path_coords,
                'start': path_coords[0],
                'end': path_coords[-1]
            })
            
        return map_data
    except Exception as e:
        print(f"Error generating migration map data: {e}")
        return []
