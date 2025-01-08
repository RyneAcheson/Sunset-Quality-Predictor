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
    weather_data |= get_weather_data(latitude, longitude, "Today", weather_data["sunset_hour"])
    weather_data["aqi_data"] = get_aqi_data(latitude, longitude, weather_data["unix_time"])
    print(weather_data.keys())
    weather_data |= get_area_type(latitude, longitude)
    print("Day and Time Data:", get_day_and_time(latitude, longitude, "Today"))
    print("Weather Data:", get_weather_data(latitude, longitude, "Today", weather_data["sunset_hour"]))
    print("AQI Data:", get_aqi_data(latitude, longitude, weather_data["unix_time"]))
    print("Area Type:", get_area_type(latitude, longitude))
    score, message = compute_sunset_score(weather_data)
    print(f"{message}")
    print(f"Score: {score}")

    return render_template("index.html",
                           score=score,
                           latitude=latitude,
                           longitude=longitude,
                           city=city,
                           state=state,
                           zipcode=zipcode,
                           message=message)

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

def get_weather_data(latitude, longitude, day, sunset_hour):
    url = f"http://api.weatherapi.com/v1/history.json?key={WEATHER_API_KEY}&q={latitude},{longitude}&dt={day}&hour={sunset_hour}&aqi=yes"
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
        "aqi_data": aqi_data
    }

def get_area_type(latitude, longitude):
    return {
        "area_type": "rural"
    }

    
# Create a formula to determine the quality of a sunset on a score scale of 0-1000 given a dictionary of data 
def compute_sunset_score(data):
    
    def compute_cloud_score(data, score, message):
        alpha = 2.5
        ideal_cloud_cover = 45
        cloud_cover_score = round(alpha * (100 - (abs(data["cloud_cover"] - ideal_cloud_cover))))

        estimated_cloud_height = ((data["surface_temperature_f"] - data["dew_point_f"]) / 4.4) * 1000
        lower_ideal_bound = 5000
        upper_ideal_bound = 20000
        ideal_cloud_height = 12000
        cloud_height_score = round(2.5 * (100 - ((estimated_cloud_height - ideal_cloud_height) / (upper_ideal_bound - lower_ideal_bound))**2 * 100))
        
        score += cloud_cover_score + cloud_height_score

        if 40 <= data["cloud_cover"] <= 60:
            message += f"-> Cloud cover is ideal, between 40% and 60%."
        elif 60 < data["cloud_cover"] <= 85:
            message += f"-> Cloud cover is semi-ideal, between 60% and %85."
        elif 85 < data["cloud_cover"]:
            message += f"-> Cloud cover is non-ideal, greater than 85%."
        elif 25 <= data["cloud_cover"] <= 40:
            message += f"-> Cloud cover is semi-ideal, between 25% and 40%."
        elif data["cloud_cover"] < 25:
            message += f"-> Cloud cover is non-ideal, less than 25%."

        message += f" ({data['cloud_cover']}%), Score: {cloud_cover_score}/250 \n"

        if estimated_cloud_height < 2000:
            message += f"-> Estimated cloud height is very low, <2000 feet."
        elif estimated_cloud_height < 5000:
            message += f"-> Estimated cloud height is low, <5000 feet."
        elif estimated_cloud_height < 12000:
            message += f"-> Estimated cloud height is ideal, Between 5000 and 12000 feet."
        elif estimated_cloud_height < 20000:
            message += f"-> Estimated cloud height is ideal, Between 12000 and 20000 feet."
        else:
            message += f"-> Estimated cloud height is very high, >20000 feet."

        message += f" ({estimated_cloud_height} feet), Score: {cloud_height_score}/250 \n"
        return score, message

    def compute_humidity_score(data, score, message):
        beta = 2.5
        ideal_humidity = 50
        humidity_score = round(beta * (100 - (abs(data["humidity"] - ideal_humidity))))
        score += humidity_score

        if data["humidity"] < 20:
            message += f"-> Humidity is very low, <20%."
        elif data["humidity"] < 35:
            message += f"-> Humidity is low, between 20% and 35%."
        elif data["humidity"] < 65:
            message += f"-> Humidity is ideal, between 35% and 65%."
        elif data["humidity"] < 80:
            message += f"-> Humidity is high, between 65% and 80%."
        else:
            message += f"-> Humidity is very high, >80%."
        
        message += f" ({data['humidity']}%), Score: {humidity_score}/250 \n"

        return score, message
    
    def compute_particulate_score(data, score, message):
        small_particulates = data["aqi_data"]["aqi_data"]["components"]["pm2_5"]
        large_particulates = data["aqi_data"]["aqi_data"]["components"]["pm10"]

        small_pm_score = 0
        if 10 <= small_particulates <= 30:
            small_pm_score = 100
        elif small_particulates < 10:
            small_pm_score = max(0, (small_particulates / 10) * 100)
        else:
            small_pm_score = max(0, 100 - ((small_particulates - 30) / 20) * 100)

        small_pm_score = round(small_pm_score * 1.25)

        large_pm_score = 0
        if 20 <= large_particulates <= 50:
            large_pm_score = 100
        elif large_particulates < 20:
            large_pm_score = max(0, (large_particulates / 20) * 100)
        elif large_particulates > 50:
            large_pm_score = max(0, 100 - ((large_particulates - 50) / 30) * 100)

        large_pm_score = round(large_pm_score * 1.25)

        particulate_score = small_pm_score + large_pm_score
        score += particulate_score
        
        if small_particulates < 10:
            message += "-> Very few small particulates in the air. Non-ideal"
        elif 10 <= small_particulates < 30:
            message += "-> Few small particulates in the air. Ideal" 
        elif small_particulates < 50:
            message += "-> Many small particulates in the air."
        elif small_particulates < 75:
            message += "-> Very many small particulates in the air."
        else:
            message += "-> Extreme number of small particulates in the air."

        message += f" ({small_particulates}), Score: {small_pm_score}/125 \n"

        if large_particulates < 10:
            message += "-> Very few large particulates in the air. Non-ideal"
        elif large_particulates < 20:
            message += "-> Few large particulates in the air. Non-ideal" 
        elif 20 <= large_particulates <= 50:
            message += "-> Many large particulates in the air. Ideal"
        elif large_particulates < 75:
            message += "-> Very many large particulates in the air."
        else:
            message += "-> Extreme number of large particulates in the air."

        message += f" ({large_particulates}), Score: {large_pm_score}/125 \n"

        return score, message
    
    '''
    def compute_aod_score(data, score, message):

        k, c = 
        aod_score = 0
        message += ""
        score += aod_score
        return score, message
    '''
    score, message = 0, "<------MESSAGE------>\n"
    score, message = compute_cloud_score(data, score, message)
    score, message = compute_humidity_score(data, score, message)
    score, message = compute_particulate_score(data, score, message)
    # score, message = compute_aod_score(data, score, message)

    return score, message

if __name__ == "__main__":
    app.run(debug=True)