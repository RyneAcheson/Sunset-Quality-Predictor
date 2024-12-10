import requests
import datetime
import time
import sys
import json
import pyinputplus as pyip

# Name: Ryne Acheson
# Date Started: June 26th 2023
# Date Finished:

def getData(target_date, zip_code):

    # Declare and Intialize Important Variables
    
    name = ""
    latitude = ""
    longitude = ""
    sunset_time = ""
    sunset_hour = 0
    unix_sunset_hour = 0
    humidity = 0
    aqi_data = 0
    cloud_cover = 0
    cloud_height = 0
    cloud_data = []
    surface_temperature_f = 0
    dew_point_f = 0

    # Translate the zipcode into an approximate longitude and latitude

    geocoding_url = f"OpenWeatherMap API URL"
    response = requests.get(geocoding_url)

    if response.status_code == 200:
        data = response.json()
        name = data["name"]
        latitude = data["lat"]
        longitude = data["lon"]

    else:
        print("Error occurred while fetching weather data. ")
        print(response.status_code)
        quit()
    
    if target_date == "Today":
        day = date.today()
    elif target_date == "Tomorrow":
        day = date.today() + timedelta(1)

    weather_url = f"WEATHER API"
    response = requests.get(weather_url)

    if response.status_code == 200:
        data = response.json()
        sunset_time = data["astronomy"]["astro"]["sunset"]
        print(sunset_time)
    
    else:
        print("Error occurred while fetching weather data. ")
        print(response.status_code)
        quit()

    weather_url = f"WEATHER API URL"
    response = requests.get(weather_url)

    if response.status_code == 200:
        data = response.json()
        # humidity = ___
        # cloud_cover = ___
        # wind = ___
        # surface_temperature_f = ___
        # dew_point_f = ___
    else:
        print("Error occurred while fetching sunset data. ")
        print(response.status_code)
        quit()

    sunset_hour = int(sunset_time[:2]) + 12

    unix_time = datetime.datetime.now()
    unix_time = unix_time.replace(hour=sunset_hour, minute=0, second=0, microsecond=0)
    unix_time = int(time.mktime(unix_time.timetuple()))
    if target_date == "Tomorrow":
        unix_time += 86400
    
    return

def validate_zip_code(zip_code):
    # Checks that the zip code entered is a 5-digit number, otherwise will raise an exception
    if (not zip_code.isdecimal()) or len(str(zip_code)) != 5:
        raise Exception(f"Invalid zip code entered!")
    
    url = "ZIP CODE VERTIFICATION API"
    params = {
        "codes": str(zip_code),
        "country": "us"
    }
    headers = {
        "apikey": ""
    }

    response = requests.request("GET", url, headers=headers, params=params)

    if response.json()["results"] == []:
        raise Exception(F"{zip_code} is not a valid US zipcode!")

    return
if __name__ == "__main__":
    welcome_message = ''' MESSAGE '''
    print(welcome_message)