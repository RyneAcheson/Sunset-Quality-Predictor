import pandas as pd
import os

def read_responses():

    return

print(read_responses())

def estimate_cloud_height(dew_point, surface_temperature):
    approximate_cloud_height = ((surface_temperature - dew_point) / 4.4) * 1000
    return approximate_cloud_height

def calculate_quality(humidity, pollution, cloud_data):
    summary = "------Summary------"
    score = 0
    cloud_score = 0
    humidity_score = 0
    pollution_score = 0
    

    # Pollution should make up 260 points total
    small_particles = pollution["components"]['pm2_5']
    large_particles = pollution['components']['pm10'] - small_particles
    pollution_score -= large_particles * 4.5    # I feel like large particles don't make a sunset better, only worse
    print(large_particles * 9.5)
    if small_particles < 10:
        summary += "-> Not many small particles in the air. \n"
        pollution_score += small_particles/10 * 235
    elif small_particles < 25:
        summary += "-> Few small particles in the air. \n"
        pollution_score += small_particles/25 * 260
    elif small_particles < 50:
        summary += "-> Many small particles in the air. \n"
        pollution_score += small_particles/50 * 160
    elif small_particles < 75:
        summary += "-> Lots of small particles in the air. \n"
        pollution_score += small_particles/75 * 130
    else:
        summary += "-> Extreme number of small particles in the air. \n"
        pollution_score += 100