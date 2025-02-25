#!/usr/bin/env python3
from flask import Flask, request, jsonify, render_template
import sqlite3
import os

app = Flask(__name__)

ALLOWED_MEASURES = {
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
    "Daily fine particulate matter"
}

def fetch_county_records(measure, limit):
    # Build the path to data.db (assumed to be in the same directory for Vercel)
    db_path = os.path.join(os.path.dirname(__file__), 'data.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    query = """
        SELECT State, County, State_code, County_code, Year_span, Measure_name,
               Measure_id, Numerator, Denominator, Raw_value,
               Confidence_Interval_Lower_Bound, Confidence_Interval_Upper_Bound,
               Data_Release_Year, fipscode
        FROM county_health_rankings
        WHERE Measure_name = ?
        ORDER BY Year_span DESC
        LIMIT ?
    """
    
    cursor.execute(query, (measure, limit))
    data = cursor.fetchall()
    conn.close()
    return data

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/county_data', methods=['POST'])
def process_county_data():
    req_data = request.get_json()
    if not req_data:
        return jsonify({'error': 'JSON body required'}), 400

    # Easter egg check
    if req_data.get('coffee') == 'teapot':
        return "I'm a teapot", 418

    zip_code = req_data.get('zip')
    measure = req_data.get('measure_name')
    limit = req_data.get('limit', 10)

    if not zip_code or not measure:
        return jsonify({'error': 'Both "zip" and "measure_name" are required'}), 400

    if not (isinstance(zip_code, str) and len(zip_code) == 5 and zip_code.isdigit()):
        return jsonify({'error': 'ZIP code must be a 5-digit string'}), 400

    if measure not in ALLOWED_MEASURES:
        return jsonify({'error': 'Invalid measure_name'}), 400

    if not isinstance(limit, int) or limit < 1:
        return jsonify({'error': 'Limit must be an integer greater than 0'}), 400

    try:
        records = fetch_county_records(measure, limit)
    except Exception as err:
        return jsonify({'error': str(err)}), 500

    if not records:
        return jsonify({'error': f'No records found for measure: {measure}'}), 404

    # Map the database columns to JSON keys
    keys = [
        "state", "county", "state_code", "county_code", "year_span", "measure_name",
        "measure_id", "numerator", "denominator", "raw_value",
        "confidence_interval_lower_bound", "confidence_interval_upper_bound",
        "data_release_year", "fipscode"
    ]
    output = [dict(zip(keys, row)) for row in records]
    return jsonify(output), 200

if __name__ == '__main__':
    app.run(debug=True)

handler = app
