import requests
from datetime import datetime, timedelta

# Soil sensor ESP32 IP address and endpoint
soil_esp32_ip = "192.168.137.8"
soil_url = f'http://{soil_esp32_ip}/handledata'

# FastAPI service endpoint
soil_api_url = "http://nabil.ddns.net:8000/soil-predict/"

def fetch_soil_data():
    try:
        response = requests.get(soil_url)
        if response.status_code == 200:
            data = response.text.strip()
            # Parse the comma-separated response
            temperature, humidity, ph = map(float, data.split(","))
            return temperature, humidity, ph
        else:
            print("Error fetching soil data:", response.text)
            return None, None, None
    except Exception as e:
        print("Error during soil data fetch:", e)
        return None, None, None

def send_soil_data_to_api(temperature, humidity, ph):
    try:
        payload = {
            "temperature": temperature,
            "humidity": humidity,
            "ph": ph
        }
        response = requests.post(soil_api_url, json=payload)

        if response.status_code == 200:
            result = response.json()
            return result.get("Recommended Crop", "Unknown")
        else:
            print("Error in soil prediction response:", response.text)
            return None
    except Exception as e:
        print("Error during soil prediction:", e)
        return None

def process_soil_data():
    """Fetch soil data and process it."""
    last_soil_check = datetime.now() - timedelta(seconds=10)  # Start time to allow immediate first check

    while True:
        try:
            # Check if 10 seconds have passed since the last soil data fetch
            current_time = datetime.now()
            if (current_time - last_soil_check).total_seconds() >= 10:
                temperature, humidity, ph = fetch_soil_data()
                if temperature is not None and humidity is not None and ph is not None:
                    print(f"Soil Data - Temp: {temperature}, Humidity: {humidity}, pH: {ph}")

                    # Send soil data to FastAPI
                    recommended_crop = send_soil_data_to_api(temperature, humidity, ph)
                    if recommended_crop:
                        print("Recommended Crop:", recommended_crop)

                # Update the last soil check timestamp
                last_soil_check = current_time

        except Exception as e:
            print("Error in soil data processing:", e)

if __name__ == "__main__":
    process_soil_data()
