#!/usr/bin/env python3
from flask import Flask, request, jsonify, render_template
import sqlite3
import os

app = Flask(__name__)

VALID_MEASURES = {
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

@app.route('/')
def show_home():
    return render_template('home.html')

@app.route('/county_data', methods=['GET'])
def show_index():
    return render_template('index.html')

@app.route('/county_data', methods=['POST'])
def get_county_data():
    try:
        payload = request.get_json()
        if payload is None:
            return jsonify({"error": "No JSON payload provided"}), 400

        # Easter egg check
        if payload.get("coffee") == "teapot":
            return "I'm a teapot", 418

        zip_code = payload.get("zip")
        measure = payload.get("measure_name")

        if not zip_code or not measure:
            return jsonify({"error": "Missing required parameters: zip and measure_name"}), 400

        if not (isinstance(zip_code, str) and len(zip_code) == 5 and zip_code.isdigit()):
            return jsonify({"error": "ZIP code must be a 5-digit string"}), 400

        if measure not in VALID_MEASURES:
            return jsonify({"error": "Invalid measure_name"}), 400

        # Connect to the SQLite database (located one directory up)
        db_path = os.path.join(os.path.dirname(__file__), '..', 'data.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        sql_query = """
            SELECT State, County, State_code, County_code, Year_span, Measure_name,
                   Measure_id, Numerator, Denominator, Raw_value,
                   Confidence_Interval_Lower_Bound, Confidence_Interval_Upper_Bound,
                   Data_Release_Year, fipscode
            FROM county_health_rankings
            WHERE Measure_name = ?
            ORDER BY Year_span DESC
        """
        cursor.execute(sql_query, (measure,))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return jsonify({"error": f"No data found for measure {measure}"}), 404

        # Map query result to dictionary keys
        keys = [
            "state", "county", "state_code", "county_code", "year_span",
            "measure_name", "measure_id", "numerator", "denominator", "raw_value",
            "confidence_interval_lower_bound", "confidence_interval_upper_bound",
            "data_release_year", "fipscode"
        ]
        results = [dict(zip(keys, row)) for row in rows]
        return jsonify(results)

    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

if __name__ == '__main__':
    app.run(debug=True)
