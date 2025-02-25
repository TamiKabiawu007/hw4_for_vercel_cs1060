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
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Easter egg: respond with HTTP 418 if "coffee" equals "teapot"
        if data.get("coffee") == "teapot":
            return "I'm a teapot", 418

        # Validate required fields
        zip_code = data.get("zip")
        measure_name = data.get("measure_name")
        
        if not zip_code or not measure_name:
            return jsonify({"error": "Missing required parameters: zip and measure_name"}), 400

        if not (isinstance(zip_code, str) and re.fullmatch(r"\d{5}", zip_code)):
            return jsonify({"error": "ZIP code must be a 5-digit string"}), 400

        if measure_name not in ALLOWED_MEASURES:
            return jsonify({"error": "Invalid measure_name"}), 400

        # Connect to the SQLite database (assumed to be one directory up)
        db_path = os.path.join(os.path.dirname(__file__), '..', 'data.db')
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        # Query zip_county to get county information for the given ZIP
        cur.execute("""
            SELECT county, county_code, default_state, state_abbreviation
            FROM zip_county
            WHERE zip = ?
            LIMIT 1
        """, (zip_code,))
        zip_row = cur.fetchone()
        if not zip_row:
            conn.close()
            return jsonify({"error": f"No county found for ZIP {zip_code}"}), 404

        county, county_code, default_state, state_abbreviation = zip_row

        # Query county_health_rankings for matching records
        cur.execute("""
            SELECT State, County, State_code, County_code, Year_span, Measure_name,
                   Measure_id, Numerator, Denominator, Raw_value,
                   Confidence_Interval_Lower_Bound, Confidence_Interval_Upper_Bound,
                   Data_Release_Year, fipscode
            FROM county_health_rankings
            WHERE Measure_name = ?
              AND county_code = ?
              AND State = ?
            ORDER BY Year_span DESC
        """, (measure_name, county_code, default_state))
        rows = cur.fetchall()
        conn.close()

        if not rows:
            return jsonify({"error": f"No data found for ZIP {zip_code} and measure {measure_name}"}), 404

        # Map the query result into a list of dictionaries
        columns = [
            "state", "county", "state_code", "county_code", "year_span", "measure_name",
            "measure_id", "numerator", "denominator", "raw_value",
            "confidence_interval_lower_bound", "confidence_interval_upper_bound",
            "data_release_year", "fipscode"
        ]
        results = [dict(zip(columns, row)) for row in rows]
        return jsonify(results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
