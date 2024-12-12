import os
import requests
import io
import urllib.request
from datetime import datetime
from PIL import Image
import matplotlib.pyplot as plt

esp32cam_ip = "nabil.ddns.net:8080/files" ## dummy server

# ESP32-CAM IP address and endpoint
#esp32cam_ip = "192.168.137.197"
cam_url = f'http://{esp32cam_ip}/cam-hi.jpg'

# FastAPI service endpoint
leaf_api_url = "http://nabil.ddns.net:8000/leaf-predict/"

# Directory to save images
image_save_dir = "captured_images"
if not os.path.exists(image_save_dir):
    os.makedirs(image_save_dir)

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
            print("Error in leaf prediction response:", response.text)
            return None
    except Exception as e:
        print("Error during leaf classification:", e)
        return None

def display_image(image):
    rotated_image = image.rotate(0)
    plt.imshow(rotated_image)
    plt.axis("off")
    plt.show(block=False)
    plt.pause(5)  # Minimal delay to keep GUI responsive
    plt.close()

def process_images():
    """Capture and process image from the camera."""
    while True:
        try:
            # Capture and process the image
            img_resp = urllib.request.urlopen(cam_url)
            img_data = img_resp.read()
            image = Image.open(io.BytesIO(img_data))
            rotated_image = image.rotate(180)

            # Save and display the image
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            image_path = os.path.join(image_save_dir, f"{timestamp}.jpg")
            rotated_image.save(image_path, format='JPEG')
            print(f"Image saved as: {image_path}")
            display_image(rotated_image)

            # Classify the leaf image
            class_label = classify_leaf_image(rotated_image)
            if class_label:
                print("Leaf Classification:", class_label)

        except Exception as e:
            print("Error in image processing:", e)

if __name__ == "__main__":
    process_images()
