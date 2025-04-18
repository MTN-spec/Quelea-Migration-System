from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import os
from models.database_utils import initialize_database, query_migration_records
from models.model_utils import simulate_migration, train_ml_model
from models.warning_utils import get_weather_forecast, predict_migration_likelihood

app = Flask(__name__)

# Database path
DB_PATH = os.path.join(os.getcwd(), 'database', 'Quelea_Birds.db')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/database', methods=['GET', 'POST'])
def database():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'initialize':
            conn = sqlite3.connect(DB_PATH)
            initialize_database(conn)
            conn.close()
        elif action == 'query':
            conn = sqlite3.connect(DB_PATH)
            records = query_migration_records(conn)
            conn.close()
            return render_template('database.html', records=records)
    return render_template('database.html')

@app.route('/simulate', methods=['GET', 'POST'])
def simulate():
    if request.method == 'POST':
        # Handle simulation parameters and visualization logic
        pass
    return render_template('simulation.html')

@app.route('/warnings', methods=['GET', 'POST'])
def warnings():
    if request.method == 'POST':
        # Handle weather forecast input and prediction logic
        pass
    return render_template('warnings.html')

if __name__ == '__main__':
    # Retrieve the PORT environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
