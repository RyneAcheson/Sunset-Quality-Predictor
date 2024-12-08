import requests
import datetime
import time
import sys
import json
import pyinputplus as pyip

# Name: Ryne Acheson
# Date Started: June 26th 2023
# Date Finished:


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