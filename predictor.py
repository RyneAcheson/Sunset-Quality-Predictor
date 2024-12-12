from flask import Flask, request, jsonify
import requests

# Name: Ryne Acheson
# Date Started: June 26th 2023
# Date Finished:

def get_sunset_score():
    zipcode = request.args.get("zip")
    if not zipcode:
        return jsonify({"error": "Invalid Zip Code Provided"}), 400
    
    latitude, longitude = geocode_zip(zipcode)

    weather_data = get_weather_data(latitude, longitude)

    score = compute_sunset_score(weather_data)

    location_type = determine_location_type(latitude, longitude)

    return jsonify({"score": score, "location_type": location_type})

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