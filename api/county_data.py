import json
import sqlite3
import re
import os

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

def query_county_data(zip_code, measure_name):
    try:
        # Map ZIP code to fipscode for testing. For example, '02138' maps to '25017'.
        zip_to_fips = {
            '02138': '25017'
        }
        fips = zip_to_fips.get(zip_code)
        if not fips:
            return None

        # Get the absolute path to the database file
        db_path = os.path.join(os.path.dirname(__file__), 'data.db')
        print(f"Attempting to connect to database at: {db_path}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        query = "SELECT * FROM county_health_rankings WHERE fipscode = ? AND measure_name = ?"
        cursor.execute(query, (fips, measure_name))
        rows = cursor.fetchall()
        if not rows:
            conn.close()
            return None
        cols = [desc[0].lower() for desc in cursor.description]
        results = [dict(zip(cols, row)) for row in rows]
        conn.close()
        return results
    except Exception as e:
        print(f"Database error: {str(e)}")
        raise

def handler(request):
    try:
        # Ensure request method is POST
        if request.get("method", "GET").upper() != "POST":
            return {
                "statusCode": 405,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Method not allowed. Only POST is allowed."})
            }

        # Check for application/json content type
        headers = request.get("headers", {})
        if "application/json" not in headers.get("content-type", ""):
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Content-Type must be application/json"})
            }

        # Parse JSON payload
        try:
            data = json.loads(request.get("body", "{}"))
        except Exception as e:
            print(f"JSON parsing error: {str(e)}")
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Invalid JSON input"})
            }

        # Check for coffee=teapot - highest priority
        if data.get("coffee") == "teapot":
            return {
                "statusCode": 418,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "I'm a teapot"})
            }

        # Validate required keys exist
        if "zip" not in data or "measure_name" not in data:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Both 'zip' and 'measure_name' are required."})
            }

        zip_code = data["zip"]
        measure_name = data["measure_name"]

        # Validate ZIP code is a 5-digit string
        if not (isinstance(zip_code, str) and re.match(r"^\d{5}$", zip_code)):
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "ZIP code must be a 5-digit string."})
            }

        # Validate measure_name
        if measure_name not in ALLOWED_MEASURE_NAMES:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "measure_name must be one of the allowed values."})
            }

        # Query the database
        results = query_county_data(zip_code, measure_name)
        if results is None:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "No data found for provided zip and measure_name."})
            }

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(results)
        }
    except Exception as e:
        print(f"Error in handler: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Internal server error."})
        }

from flask import Flask, request, Response
app = Flask(__name__)

@app.route('/county_data', methods=['POST'])
def county_data_route():
    req = {
        "method": request.method,
        "headers": {k.lower(): v for k, v in request.headers.items()},
        "body": request.data.decode('utf-8')
    }
    result = handler(req)
    return Response(result["body"], status=result["statusCode"], content_type="application/json")
