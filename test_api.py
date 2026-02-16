import requests

# Project Data
API_KEY = "c4b30cff4909985c9cbb2683f933306e"
CITY = "Bogota"  # You can change this to any city

# URL Construction
url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

print(f"--- Testing OpenWeather connection for {CITY} ---")

try:
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        print("✅ SUCCESS! Your API Key is active and working.")
        print(f"Current weather: {data['weather'][0]['description']}")
        print(f"Temperature: {data['main']['temp']}°C")
    elif response.status_code == 401:
        print("❌ Error 401: API Key is not yet active.")
        print("Note: OpenWeather can take between 30 min to 2 hours to activate new keys.")
    else:
        print(f"⚠️ Error {response.status_code}: {data.get('message', 'Unknown error')}")

except Exception as e:
    print(f"🚨 A network error occurred: {e}")