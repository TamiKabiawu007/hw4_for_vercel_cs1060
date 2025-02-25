import json
import sqlite3
import re
import os
from flask import Flask, render_template, request, jsonify

# Initialize Flask app with correct template folder
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=template_dir)

ALLOWED_MEASURE_NAMES = [
    "Violent crime rate",
    "Unemployment",
    "Children in poverty",
    "Diabetic screening",
    "Mammography screening",
    "Preventable hospital stays",
    "Uninsured",
    "Sexually transmitted infections",
    "Physical inactivity",
    "Adult obesity",
    "Premature Death",
    "Daily fine particulate matter",
]

def query_county_data(measure_name, limit):
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data.db')
    print(f"Connecting to database at: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    query = """
        SELECT State,
               County,
               State_code,
               County_code,
               Year_span,
               Measure_name,
               Measure_id,
               Numerator,
               Denominator,
               Raw_value,
               Confidence_Interval_Lower_Bound,
               Confidence_Interval_Upper_Bound,
               Data_Release_Year,
               fipscode
        FROM county_health_rankings
        WHERE Measure_name = ?
        ORDER BY Year_span DESC
        LIMIT ?
    """
    cursor.execute(query, (measure_name, limit))
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        return None
    columns = [
        "state", "county", "state_code", "county_code", "year_span",
        "measure_name", "measure_id", "numerator", "denominator", "raw_value",
        "confidence_interval_lower_bound", "confidence_interval_upper_bound",
        "data_release_year", "fipscode"
    ]
    return [dict(zip(columns, row)) for row in rows]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/county_data', methods=['POST'])
def county_data():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    data = request.get_json()

    # Teapot Easter egg
    if data.get("coffee") == "teapot":
        return jsonify({"error": "I'm a teapot"}), 418

    # Validate required fields
    if "zip" not in data or "measure_name" not in data:
        return jsonify({"error": "Both 'zip' and 'measure_name' are required."}), 400

    zip_code = data["zip"]
    measure_name = data["measure_name"]
    limit = data.get("limit", 10)

    # Validate ZIP: must be a 5-digit string
    if not (isinstance(zip_code, str) and re.match(r"^\d{5}$", zip_code)):
        return jsonify({"error": "ZIP code must be a 5-digit string."}), 400

    # Validate measure_name against allowed values
    if measure_name not in ALLOWED_MEASURE_NAMES:
        return jsonify({"error": "Invalid measure_name."}), 400

    # Validate limit is an integer >= 1
    if not (isinstance(limit, int) and limit >= 1):
        return jsonify({"error": "Limit must be a positive integer."}), 400

    # Query the database
    results = query_county_data(measure_name, limit)
    if results is None:
        return jsonify({"error": f"No data found for measure {measure_name}"}), 404

    return jsonify(results)

# This is for local development
if __name__ == '__main__':
    app.run(debug=True)

# This is for Vercel
app = app.wsgi_app
