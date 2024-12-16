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

ZIP_CODE_API_KEY = os.getenv("ZIP_CODE_API_KEY")
if not ZIP_CODE_API_KEY:
    raise ValueError("No ZIP_CODE_API_KEY set for Flask application")

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/check_sunset", methods=["POST"])
def check_sunset():
    zipcode = request.form.get("zipcode")
    if not zipcode or not zipcode.isdecimal() or len(zipcode) != 5:
        return render_template("index.html", error="Please enter a valid ZIP Code")
    
    zip_code_info = geocode_zip(zipcode)
    latitude = zip_code_info["latitude"]
    longitude = zip_code_info["longitude"]
    city = zip_code_info["city"]
    state = zip_code_info["state"]

    if latitude is None or longitude is None:
        return render_template("index.html", error="Invalid ZIP Code Provided")
    
    weather_data = get_weather_data(latitude, longitude)
    score = compute_sunset_score(weather_data)
    location_type = determine_location_type(latitude, longitude)

    return render_template("index.html",
                           score=score,
                           latitude=latitude,
                           longitude=longitude,
                           location_type=location_type,
                           city=city,
                           state=state,
                           zipcode=zipcode)

def geocode_zip(zip_code, country_code="us"):
    print(zip_code)
    url = "https://api.zipcodestack.com/v1/search"
    params = {
        "codes" : zip_code,
        "country" : country_code
    }
    headers = {
        "apikey": ZIP_CODE_API_KEY
    }

    response = requests.request('GET', url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        print(data)
        if data["results"] == []:
            return None, None
        latitude = data["results"][zip_code][0]["latitude"]
        longitude = data["results"][zip_code][0]["longitude"]
        city = data["results"][zip_code][0]["city"]
        state = data["results"][zip_code][0]["state"]

        info = {
            "latitude": latitude,
            "longitude": longitude,
            "city": city,
            "state": state
        }

        return info
    else:
        print(f"Geocoding failed for ZIP: {zip_code}. Status Code: {response.status_code}")

    return None, None

def get_weather_data(latitude, longitude):

    url = ""
    response = requests.reqest(url)
    if response.status_code == 200:
        print("good")
    else:
        print("bad")
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