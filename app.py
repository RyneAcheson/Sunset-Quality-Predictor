from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import os
import requests
import datetime
import time

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

OPEN_WEATHER_API_KEY = os.getenv("OPEN_WEATHER_API_KEY")
if not OPEN_WEATHER_API_KEY:
    raise ValueError("No OPEN_WEATHER_API_KEY set for Flask application")

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
    
    weather_data = {}
    weather_data |= get_day_and_time(latitude, longitude, "Today")
    weather_data |= get_weather_data(latitude, longitude, "Today", weather_data["sunset_time"])
    weather_data != get_aqi_data(latitude, longitude, weather_data["unix_time"])
    weather_data |= get_aod(latitude, longitude)
    print(weather_data)
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

def get_day_and_time(latitude, longitude, target_day):

    if target_day == "Today":
        day = datetime.date.today()
    elif target_day == "Tomorrow":
        day = datetime.date.today() + datetime.timedelta(1)

    url = f"http://api.weatherapi.com/v1/astronomy.json?key={WEATHER_API_KEY}&q={latitude},{longitude}&dt={day}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        sunset_time = data["astronomy"]["astro"]["sunset"]
        sunset_hour = int(sunset_time[:2]) + 12
        unix_time = datetime.datetime.now()
        unix_time = unix_time.replace(hour=sunset_hour, minute=0, second=0, microsecond=0)
        unix_time = int(time.mktime(unix_time.timetuple()))

        print(sunset_time)
        print(unix_time)
    else:
       print("Error occurred while fetching the sunset time. ")
       print(response.status_code)
       quit()
    
    return {
        "sunset_time": sunset_time,
        "sunset_hour": sunset_hour,
        "unix_time": unix_time,
        "day": day
    }

def get_weather_data(latitude, longitude, day, sunset_time):
    url = f"http://api.weatherapi.com/v1/history.json?key={WEATHER_API_KEY}&q={latitude},{longitude}&dt={day}&hour={sunset_time}&aqi=yes"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        humidity = data['forecast']['forecastday'][0]['hour'][0]['humidity']
        cloud_cover = data['forecast']['forecastday'][0]['hour'][0]['cloud']
        wind = data['forecast']['forecastday'][0]['hour'][0]['wind_mph']
        surface_temperature_f = data['forecast']['forecastday'][0]['hour'][0]['temp_f']
        dew_point_f = data['forecast']['forecastday'][0]['hour'][0]['dewpoint_f']
        print(f"HUMIDITY: {humidity}")
        print(f"CLOUD COVER %: {cloud_cover}")

    else:
        print("Error occurred while gathering weather data")
        print(response.status_code)
        quit()
    
    return {
        "data": data,
        "humidity": humidity,
        "cloud_cover": cloud_cover,
        "wind": wind,
        "surface_temperature_f": surface_temperature_f,
        "dew_point_f": dew_point_f,
    }

def get_aqi_data(latitude, longitude, unix_time):
    url = f"http://api.openweathermap.org/data/2.5/air_pollution/forecast?lat={latitude}&lon={longitude}&appid={OPEN_WEATHER_API_KEY}"
    response = requests.get(url)
    aqi_data = 0
    if response.status_code == 200:
        data = response.json()
        for i in range(48):
            if data['list'][i]['dt'] == unix_time:
                aqi_data = data['list'][i]
                continue
        print(aqi_data)
    
    else:
        print("Error occurred while fetching AQI. ")
        print(response.status_code)
        quit()

    return {
        "aqi_data": 0
    }

def get_aod(latitude, longitude):
    return {
        "aod": 0
    }

    
# Create a formula to determine the quality of a sunset on a score scale of 0-1000 given a dictionary of data 
def compute_sunset_score(data):
    score = 0
    return score

# Either using an API or some other way, determine the location type (urban, suburban, city, rural, beach)
def determine_location_type(latitude, longitude):
    return "beach"

if __name__ == "__main__":
    app.run(debug=True)