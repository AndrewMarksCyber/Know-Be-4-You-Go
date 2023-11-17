import os
import requests
from datetime import datetime, timedelta
from twilio.rest import Client
import re

# Constants
WEATHER_API_KEY = "PirateWeatherAPIKeyHere"
GOOGLE_ROUTES_API_KEY = "GoogleRoutesAPIKeyHere"
ORIGIN_LATITUDE = ""    # Example latitude (30.000)
ORIGIN_LONGITUDE = ""  # Example longitude (-80.000)
DESTINATION_LATITUDE = ""    # Example latitude 30.000
DESTINATION_LONGITUDE = ""  # Example longitude -80.000

# Helper Functions
def get_future_time_str(minutes):
    # Get future time in ISO 8601 string format.
    future_time = datetime.utcnow() + timedelta(minutes=minutes)
    return future_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

def get_weather():
    # Retrieve weather data from PirateWeather API.
    url = f"http://api.pirateweather.net/forecast/{WEATHER_API_KEY}/{ORIGIN_LATITUDE},{ORIGIN_LONGITUDE}&units=us"
    response = requests.get(url)
    if response.status_code == 200:
        weather_data = response.json()
        temp = weather_data['currently']['temperature']
        conditions = weather_data['currently']['summary']
        return temp, conditions
    return None, None

def get_route_duration():
    # Retrieve route duration from Google Routes API.
    url = "https://routes.googleapis.com/directions/v2:computeRoutes"
    headers = {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': GOOGLE_ROUTES_API_KEY,
        'X-Goog-FieldMask': 'routes.duration,routes.distanceMeters,routes.polyline.encodedPolyline'
    }
    data = {
        "origin": {"location": {"latLng": {"latitude": float(ORIGIN_LATITUDE), "longitude": float(ORIGIN_LONGITUDE)}}},
        "destination": {"location": {"latLng": {"latitude": float(DESTINATION_LATITUDE), "longitude": float(DESTINATION_LONGITUDE)}}},
        "travelMode": "DRIVE",
        "routingPreference": "TRAFFIC_AWARE",
        "departureTime": get_future_time_str(2),
        "computeAlternativeRoutes": False,
        "routeModifiers": {"avoidTolls": False, "avoidHighways": False, "avoidFerries": False},
        "languageCode": "en-US",
        "units": "IMPERIAL"
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        response_data = response.json()
        try:
            duration = response_data['routes'][0]['duration']
            duration_seconds = int(re.search(r'\d+', duration).group())
            return round(duration_seconds / 60, 2)
        except KeyError:
            return None
    return None

# Main Logic
current_temperature, current_conditions = get_weather()
if current_temperature and current_conditions:
    commute_time = get_route_duration()
    if commute_time:
        # Twilio SMS
        account_sid = 'SID'
        auth_token = 'AUTHTOKEN'
        client = Client(account_sid, auth_token)

        message = client.messages.create(
            body=f'Weather: {current_temperature}°F and {current_conditions}.\n\nCommute: {commute_time} minutes',
            from_='+1NUMBERHERE',
            to='+1NUMBERHERE'
        )
        print(message.sid)
    else:
        print("Failed to retrieve commute time.")
else:
    print("Failed to retrieve weather data.")