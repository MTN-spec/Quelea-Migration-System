import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from scipy.spatial.distance import euclidean

# Function to connect to the SQLite database
def connect_to_database(db_path):
    """
    Connect to an existing SQLite database located at the specified path.

    Parameters:
        db_path (str): The full path to the SQLite database file.

    Returns:
        Connection object or None
    """
    import sqlite3
    try:
        conn = sqlite3.connect(db_path)
        print(f"Successfully connected to the database at: {db_path}")
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to the database: {e}")
        return None

# Function to load migration data from the database
def load_migration_data(conn):
    """
    Load migration data from the SQLite database.

    Parameters:
        conn: The database connection object.

    Returns:
        DataFrame containing migration data.
    """
    try:
        query = "SELECT * FROM migration_data"
        df = pd.read_sql_query(query, conn)
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        return df
    except Exception as e:
        print(f"Error loading migration data: {e}")
        return None

# Function to predict bird migration likelihood
def predict_migration_likelihood(model, X):
    """
    Predict the migration likelihood using a trained machine learning model.

    Parameters:
        model: The trained ML model.
        X (DataFrame): Input features for prediction.

    Returns:
        Predicted values (array).
    """
    return model.predict(X)

# Train a Random Forest model
def train_ml_model(X, y):
    """
    Train a Random Forest model.

    Parameters:
        X (array-like): Input features.
        y (array-like): Target values.

    Returns:
        Trained Random Forest model.
    """
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    print(f"Model MSE: {mse}")
    return model

# Function to calculate Euclidean distance
def calculate_distance(point1, point2):
    """
    Calculate the Euclidean distance between two points.

    Parameters:
        point1, point2 (array-like): Coordinates of the two points.

    Returns:
        Euclidean distance.
    """
    return euclidean(point1, point2)

# Function to simulate migration paths
def simulate_migration(parameters_df, num_steps=100, x_min=31.794, x_max=32.335, y_min=-20.918, y_max=-19.948):
    """
    Simulate migration paths based on parameters from the database.

    Parameters:
        parameters_df (DataFrame): DataFrame containing migration parameters.
        num_steps (int): Number of steps in the simulation.

    Returns:
        List of migration paths.
    """
    paths = []
    for idx, row in parameters_df.iterrows():
        pos = np.array([row['longitude'], row['latitude']])
        path = [pos.copy()]
        drift_strength = row.get('drift_strength', 0.05)
        noise_std = row.get('noise_std', 0.01)
        for _ in range(num_steps):
            drift = drift_strength * np.random.uniform(-1, 1, 2)
            noise = np.random.normal(0, noise_std, 2)
            pos = pos + drift + noise
            pos[0] = np.clip(pos[0], x_min, x_max)
            pos[1] = np.clip(pos[1], y_min, y_max)
            path.append(pos.copy())
        paths.append(path)
    return paths

# Function to aggregate features over time
def aggregate_features(paths, window_size=5):
    """
    Aggregate features over time using a rolling window.

    Parameters:
        paths (list): List of migration paths.
        window_size (int): Size of the rolling window.

    Returns:
        List of aggregated features.
    """
    aggregated_features = []
    for path in paths:
        path_features = []
        for i in range(len(path) - window_size):
            window = path[i:i + window_size]
            mean_x = np.mean([p[0] for p in window])
            mean_y = np.mean([p[1] for p in window])
            std_x = np.std([p[0] for p in window])
            std_y = np.std([p[1] for p in window])
            path_features.append([mean_x, mean_y, std_x, std_y])
        aggregated_features.append(path_features)
    return aggregated_features

# Function to fetch weather forecast data
def get_weather_forecast():
    """
    Simulate fetching weather forecast data.

    Returns:
        A dictionary with weather data.
    """
    # Example: Return simulated weather data
    return {
        "rainfall_mm": np.random.uniform(0, 100),
        "temperature_c": np.random.uniform(15, 35),
        "humidity_percent": np.random.uniform(40, 80),
        "wind_speed_m_s": np.random.uniform(0, 15),
        "altitude_m": np.random.uniform(1000, 2000)
    }
