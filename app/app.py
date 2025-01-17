﻿from flask import Flask, request, render_template
import requests
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def home():
    return render_template('index.html')  # Render index.html

# API keys
WEATHER_API_KEY = '93980c5df83ff5b63ff872da7dd478ea'
WEATHER_BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

FLIGHTS_API_KEY = "fdbe84ce39bc2cf61895e80bf3c6f9f3"
FLIGHTS_BASE_URL = "https://api.aviationstack.com/v1/flights"
FUTURE_FLIGHTS_BASE_URL = "https://api.aviationstack.com/v1/flightsFuture"

CITY_TO_IATA = {
    'Sofia': 'SOF',
    'New York': 'JFK',
    'London': 'LHR',
    'Berlin': 'TXL',
    'Paris': 'CDG',
    'Tokyo': 'HND',
    'Dubai': 'DXB',
    'Moscow': 'SVO',
    'Los Angeles': 'LAX',
    'Chicago': 'ORD',
    'San Francisco': 'SFO',
    'Miami': 'MIA'
}

def kelvin_to_celsius(temp_k):
    return round(temp_k - 273.15)

@app.route('/weather', methods=['GET'])
def get_weather():
    city = request.args.get('city')
    try:
        response = requests.get(f"{WEATHER_BASE_URL}?q={city}&appid={WEATHER_API_KEY}")
        if response.status_code == 200:
            response.encoding = 'utf-8'  # Ensure UTF-8 encoding
            data = response.json()  # Use built-in JSON decoding
            temp = kelvin_to_celsius(data['main']['temp'])
            weather_description = data['weather'][0]['description']
            # Return a plain-text response
            return f"Weather in {city}:\nTemperature: {temp}°C\nDescription: {weather_description}", 200
        else:
            logging.error(f"Failed to fetch weather data for {city}: {response.text}")
            return f"Error: Failed to fetch weather data for {city}", 400
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/flights', methods=['GET'])
def get_flights():
    arrival_city = request.args.get('arrival_city')
    departure_city = request.args.get('departure_city')

    arrival_iata = CITY_TO_IATA.get(arrival_city)
    departure_iata = CITY_TO_IATA.get(departure_city)

    if not arrival_iata or not departure_iata:
        return "Error: Invalid city name.", 400

    try:
        response = requests.get(f"{FLIGHTS_BASE_URL}?access_key={FLIGHTS_API_KEY}&arr_iata={arrival_iata}&dep_iata={departure_iata}")
        if response.status_code == 200:
            data = response.json()  # Use built-in JSON decoding
            flights = []
            for flight in data.get('data', [])[:10]:
                flights.append(
                    f"Airline: {flight['airline']['name']}, Flight Number: {flight['flight']['number']}, "
                    f"Date: {flight['flight_date']}, Status: {flight.get('flight_status', 'N/A')}"
                )
            return "\n".join(flights), 200
        else:
            logging.error(f"Failed to fetch flight data: {response.text}")
            return "Error: Failed to fetch flight data.", 400
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/future-flights', methods=['GET'])
def get_future_flights():
    departure_city = request.args.get('departure_city')
    arrival_city = request.args.get('arrival_city')
    flight_date = request.args.get('flight_date')

    departure_iata = CITY_TO_IATA.get(departure_city)
    arrival_iata = CITY_TO_IATA.get(arrival_city)

    if not departure_iata or not arrival_iata:
        return "Error: Invalid city name.", 400

    try:
        response = requests.get(f"{FUTURE_FLIGHTS_BASE_URL}?access_key={FLIGHTS_API_KEY}&iataCode={departure_iata}&type=departure&date={flight_date}")
        if response.status_code == 200:
            data = response.json()  # Use built-in JSON decoding
            flights = []
            for flight in data.get('data', [])[:10]:
                airline_name = flight['airline']['name'].title()
                flights.append(
                    f"Airline: {airline_name}, Flight Number: {flight['flight']['number']}, "
                    f"Departure Time: {flight['departure'].get('scheduled', 'N/A')}, Arrival Time: {flight['arrival'].get('scheduled', 'N/A')}"
                )
            return "\n".join(flights), 200
        else:
            logging.error(f"Failed to fetch future flight data: {response.text}")
            return "Error: Failed to fetch future flight data.", 400
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        return f"Error: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')