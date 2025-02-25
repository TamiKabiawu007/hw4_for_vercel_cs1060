import json
import csv
import os
import re


def handler(request):
    try:
        body = request.get_json()
    except Exception as e:
        return { "statusCode": 400, "body": "Invalid JSON" }
        
    # Check for teapot condition
    if body.get("coffee") == "teapot":
        return { "statusCode": 418, "body": "I'm a teapot" }
        
    # Check required keys
    if "zip" not in body or "measure_name" not in body:
        return { "statusCode": 400, "body": "Missing required key: zip and measure_name are required" }
        
    zip_code = str(body["zip"]).strip()
    measure = body["measure_name"].strip()
    
    # Validate zip code (must be exactly 5 digits)
    if not re.match(r"^\d{5}$", zip_code):
        return { "statusCode": 400, "body": "Invalid zip; must be 5 digits" }
        
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
    
    if measure not in allowed_measures:
        return { "statusCode": 400, "body": "Invalid measure_name" }
        
    # Load CSV data from county_health_rankings.csv
    csv_path = os.path.join(os.getcwd(), "county_health_rankings.csv")
    if not os.path.exists(csv_path):
        return { "statusCode": 500, "body": "Data file not found" }
        
    results = []
    try:
        with open(csv_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Assume the CSV has a column named 'zip' and 'measure_name'
                if row.get("zip") == zip_code and row.get("measure_name") == measure:
                    results.append(row)
    except Exception as e:
        return { "statusCode": 500, "body": "Error reading data file" }
        
    if not results:
        return { "statusCode": 404, "body": "No data found" }
        
    return {
        "statusCode": 200,
        "body": json.dumps(results),
        "headers": { "Content-Type": "application/json" }
    }
