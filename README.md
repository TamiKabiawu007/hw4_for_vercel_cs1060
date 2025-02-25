# API Prototyping with Generative AI - HW4

This repository contains:
- **csv_to_sqlite.py**: A script to load CSV files into a SQLite database (`data.db`).
- **api/county_data.py**: A Flask API endpoint that serves county health data based on a ZIP code and measure name.
- **vercel.json**: Configuration for deploying the API on Vercel.
- **link.txt**: Contains the URL of the deployed API endpoint.
- **requirements.txt**: Python dependencies.
- **.gitignore**: Standard files to ignore.

## Data Sources
- [RowZero Zip Code to County](https://rowzero.io/blog/zip-code-to-state-county-metro)
- [County Health Rankings & Roadmaps](https://www.countyhealthrankings.org/health-data)

## Usage

### Data Processing
To create the SQLite database:
```sh
rm data.db
python3 csv_to_sqlite.py data.db zip_county.csv
python3 csv_to_sqlite.py data.db county_health_rankings.csv
