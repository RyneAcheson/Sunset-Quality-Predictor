from flask import Flask, request, jsonify, render_template
import requests

# Name: Ryne Acheson
# Date Started: June 26th 2023
# Date Finished:

app = Flask(__name__)
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/check_sunset", methods=["POST"])
def check_sunset():
    zipcode = request.form.get("zipcode")
    if not zipcode or not zipcode.isdecimal() or len(zipcode) != 5 or not valid_zip(zipcode):
        return render_template("index.html", error="Please enter a valid ZIP Code")
    
    latitude, longitude = geocode_zip(zipcode)
    weather_data = get_weather_data(latitude, longitude)
    score = compute_sunset_score(weather_data)
    location_type = determine_location_type(latitude, longitude)

    return render_template("index.html",
                           score=score,
                           location_type=location_type,
                           zipcode=zipcode)

def valid_zip(zipcode):
    return True
def geocode_zip(zipcode):
    return 0, 0

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