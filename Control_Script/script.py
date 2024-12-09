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
leaf_api_url = "http://nabil.ddns.net:8000/leaf-predict/"
soil_api_url = "http://nabil.ddns.net:8000/soil-predict/"


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
            return result.get("predicted_class", "Unknown"), "leaf"
        else:
            print("Error in FastAPI response:", response.text)
            return None, None

    except Exception as e:
        print("Error during leaf classification:", e)
        return None, None


##def send_classification_to_esp32(class_label):
##    payload = {'class_label': str(class_label)}
##    response = requests.post(url, data=payload)
##    return response.text


while True:
    try:
        # Capture image from ESP32CAM
        img_resp = urllib.request.urlopen(cam_url)
        img_data = img_resp.read()  # Read the image data as bytes
        image = Image.open(io.BytesIO(img_data))  # Convert bytes to PIL Image
        
        #image = Image.open("test.jpg") #test

        # Send image to FastAPI for classification
        class_label, category = classify_leaf_image(image)

        if class_label is not None:
            print("Class label:", class_label)
            #print("Category:", category)
            sleep(5.0)

    except Exception as e:
        print("Error:", e)
        sleep(5.0)
