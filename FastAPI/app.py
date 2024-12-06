from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image
import numpy as np
import onnxruntime as ort

app = FastAPI()

MODEL_PATH = "plant_disease_model.onnx"
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

onnx_session = ort.InferenceSession(MODEL_PATH)

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
async def predict(file: UploadFile = File(...)):
    try:
        image = Image.open(file.file)
        input_image = preprocess_image(image)

        inputs = {onnx_session.get_inputs()[0].name: input_image.astype(np.float32)}
        outputs = onnx_session.run(None, inputs)

        predicted_class = CLASS_NAMES[np.argmax(outputs[0])]

        return JSONResponse(content={"predicted_class": predicted_class})
    
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
