# tamikabiawu007-hw4

This is a Flask-based API for county data.

## Overview

The API provides a `/county_data` endpoint that accepts HTTP POST requests with JSON data. The endpoint requires a valid 5-digit ZIP code and one of a specified list of `measure_name` values to query the county_health_rankings database. If the input includes `coffee: teapot`, the endpoint returns a 418 error. A missing or invalid input results in appropriate error responses.

## Purpose
This project is a homework assignment for CS1060. It aims to demonstrate programming proficiency by tackling real-world data processing challenges. The project, which includes modules like county_data.py, processes county-level data and applies computational techniques to derive actionable insights. The focus is on building a structured, maintainable codebase that meets the course objectives.

## Deployment

This project is configured to run on Vercel. The `vercel.json` file is set up for deploying Python functions. For more details, please refer to the Vercel documentation.

## Testing

A test suite is provided in the `tests/` directory. To run the tests, install the dependencies from `requirements.txt` and then run `pytest` from the project root.

## Getting Started

1. Install the dependencies: `pip install -r requirements.txt`
2. Run the Flask app locally with: `python -m flask run`
3. Deploy to Vercel following the instructions on Vercel's website.
