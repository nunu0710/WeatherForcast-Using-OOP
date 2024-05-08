import requests
import datetime
import json
from geopy.geocoders import Nominatim
from requests.exceptions import RequestException

class WeatherForecast:
    def __init__(self, weather_file):
        self.weather_file = weather_file
        self.data = {}

    def __setitem__(self, date, forecast):
        self.data[date] = forecast

    def __getitem__(self, date):
        return self.data[date]

    def __iter__(self):
        return iter(self.data)

    def items(self):
        return self.data.items()

    def load_from_file(self):
        try:
            with open(self.weather_file, "r") as file:
                self.data = json.load(file)
        except FileNotFoundError:
            print("File not found. No weather data loaded.")

    def save_to_file(self):
        data_str_keys = {str(key): value for key, value in self.data.items()}  # Convert date keys to strings
        with open(self.weather_file, "w") as file:
            json.dump(data_str_keys, file)

def is_valid_date(date_string, format="%Y-%m-%d"):
    try:
        datetime.datetime.strptime(str(date_string), format)  # Convert date_string to string
        return True
    except ValueError:
        return False

def get_coordinates(city):
    geolocator = Nominatim(user_agent="get_weather_prog")
    location = geolocator.geocode(city)
    if location:
        return location.latitude, location.longitude
    else:
        print("Location not found.")
        return None

weather = WeatherForecast("weather.txt")

while True:
    choice = input("Please type:\n1. for existing weather info.\n2. Other weather news\n3. To  iter\n4. To get Item\n5. To Exit\n")
    if choice == "1":
        weather.load_from_file()
        print(list(weather.items()))
    elif choice == "2":
        city = input("Enter a city name: ")
        coordinates = get_coordinates(city)
        if coordinates:
            latitude, longitude = coordinates
            print(f"The latitude and longitude of {city} are: {latitude}, {longitude}")
        else:
            continue  

        print("\n\nChoose the start and end date, and if you leave them blank it will default to the next day date!\n\n")
        start_date = input("What is the start date in this format please: yyyy-mm-dd: ")
        end_date = input("What is the end date in this format please: yyyy-mm-dd: ")

        # Default start_date and end_date to next day if empty
        if not start_date:
            start_date = datetime.date.today() + datetime.timedelta(days=1)
        if not end_date:
            end_date = datetime.date.today() + datetime.timedelta(days=1)

        if is_valid_date(start_date) and is_valid_date(end_date):
            try:
                url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&daily=precipitation_sum&timezone=Europe%2FLondon&start_date={start_date}&end_date={end_date}"
                response = requests.get(url)
                response.raise_for_status()  
                response_dict = response.json()
                precipitation_data = response_dict.get("daily", {}).get("precipitation_sum", [])
                time_data = response_dict.get("daily", {}).get("time", [])

                for sum, t in zip(precipitation_data, time_data):
                    if sum > 0:
                        print(f"On {t}, it will be raining in {city} and precipitation sum will be {sum} mm")
                    else:
                        print(f"There's no rain in {city} on {t}")

                # Store data from API response and save to file
                weather[start_date] = {"city": city, "precipitation": precipitation_data, "time": time_data}
                weather.save_to_file()

            except RequestException as e:  
                print("Failed to fetch weather data from the API:", e)

            except json.JSONDecodeError:
                print("Failed to decode JSON response from the API.")
        else:
            print("Invalid date format entered. Please use yyyy-mm-dd format.")
            continue
        
    elif choice == "3":
        print("Weather forecasts for the known dates:")
        for date in weather:
            print(f"{date}: {weather[date]}")
    elif choice == "4":
        date = input("Enter the date (yyyy-mm-dd) to get the weather forecast: ")
        if date in weather:
            print(f"{date}: {weather[date]}")
        else:
            print("Weather forecast not found for the given date.")
    elif choice == "5":
        break
    else:
        print("Invalid choice. Please try again.")
