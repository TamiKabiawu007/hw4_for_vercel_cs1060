#!/usr/bin/env python3
from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

allowed_measures = [
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
]

@app.route('/county_data', methods=['POST'])
def county_data():
    try:
        # Get JSON data from the curl request
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        # Easter egg: if JSON contains "coffee": "teapot", respond with HTTP 418
        if data.get('coffee') == 'teapot':
            return "I'm a teapot", 418

        # Validate required parameters
        zip_code = data.get('zip')
        measure_name = data.get('measure_name')

        if not zip_code or not measure_name:
            return jsonify({'error': 'Missing required parameters'}), 400

        if not (isinstance(zip_code, str) and len(zip_code) == 5 and zip_code.isdigit()):
            return jsonify({'error': 'Invalid ZIP code'}), 400

        if measure_name not in allowed_measures:
            return jsonify({'error': 'Invalid measure_name'}), 400

        # Connect to the SQLite database (data.db is expected to be one directory up)
        db_path = os.path.join(os.path.dirname(__file__), '..', 'data.db')
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        # Query the county_health_rankings table with LIMIT
        query = '''
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
        '''

        cur.execute(query, (measure_name,))
        rows = cur.fetchall()
        conn.close()

        if not rows:
            return jsonify({'error': f'No data found for measure {measure_name}'}), 404

        # Transform rows into a list of dictionaries using the county_health_rankings schema
        keys = ["state", "county", "state_code", "county_code", "year_span", "measure_name", "measure_id", "numerator", "denominator", "raw_value", "confidence_interval_lower_bound", "confidence_interval_upper_bound", "data_release_year", "fipscode"]
        results = [dict(zip(keys, map(str, row))) for row in rows]
        return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
