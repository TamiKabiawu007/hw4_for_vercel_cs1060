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

def query_county_data(measure_name, limit):
    # Build the database path (one directory up, like Version 1)
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data.db')
    print(f"Connecting to database at: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Use a query similar to Version 1 (ignoring ZIP code)
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
    # Define column names to match Version 1's schema
    columns = [
        "state", "county", "state_code", "county_code", "year_span",
        "measure_name", "measure_id", "numerator", "denominator", "raw_value",
        "confidence_interval_lower_bound", "confidence_interval_upper_bound",
        "data_release_year", "fipscode"
    ]
    return [dict(zip(columns, row)) for row in rows]

def process_request(method, headers, body):
    try:
        # Accept only POST requests
        if method.upper() != "POST":
            return {
                "statusCode": 405,
                "body": json.dumps({"error": "Method not allowed. Only POST is allowed."})
            }
        # Ensure Content-Type is application/json
        content_type = headers.get("content-type", "")
        if "application/json" not in content_type.lower():
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Content-Type must be application/json"})
            }
        # Parse the JSON payload
        try:
            data = json.loads(body)
        except Exception as e:
            print(f"JSON parsing error: {str(e)}")
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Invalid JSON input"})
            }
        # Teapot Easter egg
        if data.get("coffee") == "teapot":
            return {
                "statusCode": 418,
                "body": json.dumps({"error": "I'm a teapot"})
            }
        # Validate that both 'zip' and 'measure_name' are provided
        if "zip" not in data or "measure_name" not in data:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Both 'zip' and 'measure_name' are required."})
            }
        zip_code = data["zip"]
        measure_name = data["measure_name"]
        limit = data.get("limit", 10)
        # Validate ZIP: must be a 5-digit string
        if not (isinstance(zip_code, str) and re.match(r"^\d{5}$", zip_code)):
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "ZIP code must be a 5-digit string."})
            }
        # Validate measure_name against allowed values
        if measure_name not in ALLOWED_MEASURE_NAMES:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Invalid measure_name."})
            }
        # Validate limit is an integer >= 1
        if not (isinstance(limit, int) and limit >= 1):
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Limit must be a positive integer."})
            }
        # Query the database with the provided measure_name and limit
        results = query_county_data(measure_name, limit)
        if results is None:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": f"No data found for measure {measure_name}"})
            }
        return {
            "statusCode": 200,
            "body": json.dumps(results)
        }
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error."})
        }

def handler(request, context):
    """Vercel serverless function handler"""
    try:
        method = request.get("method", "GET")
        headers = request.get("headers", {})
        body = request.get("body", "{}")
        
        result = process_request(method, headers, body)
        
        return {
            "statusCode": result["statusCode"],
            "headers": {"Content-Type": "application/json"},
            "body": result["body"]
        }
    except Exception as e:
        print(f"Handler error: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Internal server error."})
        }
