from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from PIL import Image
import pandas as pd
import numpy as np
import onnxruntime as ort
import joblib

app = FastAPI()

# Paths to models
LEAF_MODEL_PATH = "model/leaf_disease_model.onnx"
SOIL_MODEL_PATH = "model/crop_recommendation_model.pkl"
SCALER_PATH = "model/scaler.pkl"

# Class names for leaf disease prediction
CLASS_NAMES = [
    "Apple__Apple_scab", "Apple__Black_rot", "Apple__Cedar_apple_rust", "Apple__healthy",
    "Background_without_leaves", "Bean__Blight", "Bean__Healthy", "Bean__Mosaic_Virus",
    "Bean__Rust", "Blueberry__healthy", "Cherry__Powdery_mildew", "Cherry__healthy",
    "Corn__Cercospora_leaf_spot Gray_leaf_spot", "Corn__Common_rust", "Corn__Northern_Leaf_Blight",
    "Corn__healthy", "Cowpea__Bacterial_wilt", "Cowpea__Healthy", "Cowpea__Mosaic_virus",
    "Cowpea__Septoria_leaf_spot", "Grape__Black_rot", "Grape__Esca_(Black_Measles)",
    "Grape__Leaf_blight_(Isariopsis_Leaf_Spot)", "Grape__healthy", "Orange__Haunglongbing_(Citrus_greening)",
    "Peach__Bacterial_spot", "Peach__healthy", "Pepper__bell__Bacterial_spot",
    "Pepper__bell__healthy", "Potato__Early_blight", "Potato__Late_blight", "Potato__healthy",
    "Raspberry__healthy", "Soybean__healthy", "Squash__Powdery_mildew", "Strawberry__Leaf_scorch",
    "Strawberry__healthy", "Tomato__Bacterial_spot", "Tomato__Early_blight", "Tomato__Late_blight",
    "Tomato__Leaf_Mold", "Tomato__Septoria_leaf_spot", "Tomato__Spider_mites Two-spotted_spider_mite",
    "Tomato__Target_Spot", "Tomato__Tomato_Yellow_Leaf_Curl_Virus", "Tomato__Tomato_mosaic_virus",
    "Tomato__healthy"
]

# Load ONNX session for leaf model
onnx_session = ort.InferenceSession(LEAF_MODEL_PATH)

# Load crop recommendation model and scaler
soil_model = joblib.load(SOIL_MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

# Transformation for image preprocessing
def preprocess_image(image):
    image = image.resize((224, 224)).convert("RGB")
    image = np.array(image).astype(np.float32)
    
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    image = (image / 255.0 - mean) / std

    image = image.transpose(2, 0, 1).astype(np.float32)
    image = np.expand_dims(image, axis=0)
    
    return image


@app.post("/leaf-predict/")
async def predict_leaf(file: UploadFile = File(...)):
    """Predict leaf disease."""
    try:
        image = Image.open(file.file)
        input_image = preprocess_image(image)

        inputs = {onnx_session.get_inputs()[0].name: input_image.astype(np.float32)}
        outputs = onnx_session.run(None, inputs)

        predicted_class = CLASS_NAMES[np.argmax(outputs[0])]

        return JSONResponse(content={"predicted_class": predicted_class})
    
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


class SoilInput(BaseModel):
    """Input schema for soil prediction."""
    temperature: float
    humidity: float
    ph: float


@app.post("/soil-predict/")
async def predict_soil(input_data: SoilInput):
    """Predict suitable crop based on soil data."""
    try:
        # Define the feature names based on what the scaler was fitted with
        feature_names = ["temperature", "humidity", "ph"]
        
        # Convert input data to a DataFrame with proper feature names
        features = pd.DataFrame([input_data.model_dump()], columns=feature_names)
        
        # Scale the input features
        scaled_features = scaler.transform(features)
        
        # Predict the crop
        predicted_crop = soil_model.predict(scaled_features)

        return JSONResponse(content={"Recommended Crop": predicted_crop[0]})
    
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
