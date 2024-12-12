from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import os
import requests

# Name: Ryne Acheson
# Date Started: June 26th 2023
# Date Finished:

load_dotenv()

app = Flask(__name__)

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
if not WEATHER_API_KEY:
    raise ValueError("No WEATHER_API_KEY set for Flask application")

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/check_sunset", methods=["POST"])
def check_sunset():
    zipcode = request.form.get("zipcode")
    if not zipcode or not zipcode.isdecimal() or len(zipcode) != 5 or not valid_zip(zipcode):
        return render_template("index.html", error="Please enter a valid ZIP Code")
    
    latitude, longitude = geocode_zip(zipcode)
    if latitude is None or longitude is None:
        return render_template("index.html", error="Invalid ZIP Code Provided")
    
    weather_data = get_weather_data(latitude, longitude)
    score = compute_sunset_score(weather_data)
    location_type = determine_location_type(latitude, longitude)

    return render_template("index.html",
                           score=score,
                           location_type=location_type,
                           zipcode=zipcode)

def geocode_zip(zip_code, country_code="US"):

    url = f"http://api.openweathermap.org/geo/1.0/zip"
    params = {
        "zip": f"{zip_code}, {country_code}",
        "appid": WEATHER_API_KEY
    }
    
    response = requests.get(url, params=params, timeout=10)
    if response.status_code == 200:
        data = response.json()
        latitude = data.get("lat")
        longitude = data.get("lon")
        return latitude, longitude
    else:
        print(f"Geocoding failed for ZIP: {zip_code}. Status Code: {response.status_code}")
        
def get_weather_data(latitude, longitude):
    return {
        "cloud_cover": 0,
        "cloud_height": 0,
        "humidity": 0
    }


def compute_sunset_score(data):
    score = 0
    return score

def determine_location_type(latitude, longitude):
    return "beach"

if __name__ == "__main__":
    app.run(debug=True)