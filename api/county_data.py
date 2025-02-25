import json
import sqlite3
import os
import re
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

ALLOWED_MEASURES = [
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

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/county_data', methods=['POST'])
def county_data():
    # Check content type
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Easter egg: respond with HTTP 418 if "coffee" equals "teapot"
        if data.get("coffee") == "teapot":
            return "", 418

        # Validate required fields
        zip_code = data.get("zip")
        measure_name = data.get("measure_name")
        
        if not zip_code or not measure_name:
            return jsonify({"error": "Missing required parameters: zip and measure_name"}), 400

        if not (isinstance(zip_code, str) and re.fullmatch(r"\d{5}", zip_code)):
            return jsonify({"error": "ZIP code must be a 5-digit string"}), 400

        if measure_name not in ALLOWED_MEASURES:
            return jsonify({"error": "Invalid measure_name"}), 400

        # Connect to the SQLite database
        db_path = os.path.join(os.path.dirname(__file__), '..', 'data.db')
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        # Query county_health_rankings directly using ZIP code from zip_county table
        cur.execute("""
            SELECT 
                chr.confidence_interval_lower_bound,
                chr.confidence_interval_upper_bound,
                chr.county,
                chr.county_code,
                chr.data_release_year,
                chr.denominator,
                chr.fipscode,
                chr.measure_id,
                chr.measure_name,
                chr.numerator,
                chr.raw_value,
                chr.state,
                chr.state_code,
                chr.year_span
            FROM county_health_rankings chr
            JOIN zip_county zc ON chr.county_code = zc.county_code 
                AND chr.state = zc.default_state
            WHERE zc.zip = ? AND chr.measure_name = ?
            ORDER BY chr.year_span DESC
        """, (zip_code, measure_name))
        
        rows = cur.fetchall()
        conn.close()

        if not rows:
            return jsonify({"error": f"No data found for ZIP {zip_code} and measure {measure_name}"}), 404

        # Map the query result into a list of dictionaries with exact schema matching
        results = []
        for row in rows:
            result = {
                "confidence_interval_lower_bound": row[0],
                "confidence_interval_upper_bound": row[1],
                "county": row[2],
                "county_code": row[3],
                "data_release_year": row[4],
                "denominator": row[5],
                "fipscode": row[6],
                "measure_id": row[7],
                "measure_name": row[8],
                "numerator": row[9],
                "raw_value": row[10],
                "state": row[11],
                "state_code": row[12],
                "year_span": row[13]
            }
            results.append(result)

        return jsonify(results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
