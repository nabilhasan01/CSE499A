import requests
import io
import urllib.request
import numpy as np
from PIL import Image
from time import sleep

# ESP32CAM IP address and port
esp32cam_ip = "192.168.4.1"
url = 'http://' + esp32cam_ip + '/receive_data'

# URL for capturing image from ESP32CAM
cam_url = 'http://' + esp32cam_ip + '/cam-hi.jpg'

# FastAPI service endpoints
leaf_api_url = "http://127.0.0.1:8000/leaf-predict/"
soil_api_url = "http://127.0.0.1:8000/soil-predict/"

def classify_leaf_image(image):
    try:
        # Convert PIL image to bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        # Send the image to FastAPI
        files = {'file': ('image.jpg', img_byte_arr, 'image/jpeg')}
        response = requests.post(leaf_api_url, files=files)

        if response.status_code == 200:
            result = response.json()
            return result.get("predicted_class", "Unknown")
        else:
            print("Error in FastAPI response:", response.text)
            return None

    except Exception as e:
        print("Error during leaf classification:", e)
        return None

##def send_classification_to_esp32(class_label):
##    payload = {'class_label': str(class_label)}
##    response = requests.post(url, data=payload)
##    return response.text

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
            print("Error in soil-predict response:", response.text)
            return None
    except Exception as e:
        print("Error during soil prediction:", e)
        return None

while True:
    try:
        cam_url = 'http://127.0.0.1/files/test.jpg' #Dummy cam image
        sensor_data_url = 'http://127.0.0.1/sensor-data' #Dummy Sensor Data

        # Capture image from ESP32CAM
        img_resp = urllib.request.urlopen(cam_url)
        img_data = img_resp.read()  # Read the image data as bytes
        image = Image.open(io.BytesIO(img_data))  # Convert bytes to PIL Image

        # Send image to FastAPI for classification
        class_label = classify_leaf_image(image)

        if class_label is not None:
            print("Leaf Disease Class:", class_label)
            sleep(0.5)
        
        # Fetch sensor data from ESP32
        sensor_resp = requests.get(sensor_data_url)
        if sensor_resp.status_code == 200:
            sensor_data = sensor_resp.json()
            temperature = sensor_data.get("temperature")
            humidity = sensor_data.get("humidity")
            ph = sensor_data.get("ph")

            print(f"Sensor Data - Temperature: {temperature}, Humidity: {humidity}, pH: {ph}")

            # Send sensor data to FastAPI for soil prediction
            recommended_crop = send_soil_data_to_api(temperature, humidity, ph)
            if recommended_crop is not None:
                print("Recommended Crop:", recommended_crop)
        sleep(3.0)

    except Exception as e:
        print("Error:", e)
        sleep(3.0)
