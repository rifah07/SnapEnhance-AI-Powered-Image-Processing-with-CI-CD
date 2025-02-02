from flask import Flask, request, send_from_directory, jsonify
import os
import numpy as np
import cv2
import tensorflow as tf
from PIL import Image
from flask_cors import CORS
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array, load_img
from rembg import remove  # Background removal

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

#load AI Sketch Model
model = load_model('models/sketch_model.keras')

@app.route("/")
def home():
    return jsonify({"message": "SnapEnhance API with AI & Filters is running!"})

@app.route("/upload", methods=["POST"])
def upload_image():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    file = request.files["image"]
    effect = request.form.get("effect", "sketch")  # the default effect is "sketch"

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    processed_path = os.path.join(PROCESSED_FOLDER, file.filename)

    # Load image
    img = cv2.imread(file_path)

    # apply selected effect
    if effect == "sketch":
        img = Image.open(file_path).convert("RGB")
        img = img.resize((256, 256))
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        sketch_output = model.predict(img_array)[0]
        sketch_output = (sketch_output * 255).astype(np.uint8)
        cv2.imwrite(processed_path, sketch_output)

    elif effect == "grayscale":
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(processed_path, gray)

    elif effect == "invert":
        inverted = cv2.bitwise_not(img)
        cv2.imwrite(processed_path, inverted)

    elif effect == "blur":
        blurred = cv2.GaussianBlur(img, (15, 15), 0)
        cv2.imwrite(processed_path, blurred)

    elif effect == "edge-detect":
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        cv2.imwrite(processed_path, edges)

    elif effect == "background-remove":
        img_pil = Image.open(file_path)
        img_no_bg = remove(img_pil)  #remove background
        img_no_bg.save(processed_path, "PNG")

    elif effect == "pencil-sketch":
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        inv = cv2.bitwise_not(gray)
        blur = cv2.GaussianBlur(inv, (21, 21), 0)
        sketch = cv2.divide(gray, 255 - blur, scale=256)
        cv2.imwrite(processed_path, sketch)

    elif effect == "cartoonify":
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.medianBlur(gray, 5)
        edges = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
        color = cv2.bilateralFilter(img, 9, 300, 300)
        cartoon = cv2.bitwise_and(color, color, mask=edges)
        cv2.imwrite(processed_path, cartoon)

    elif effect == "sharpen":
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        sharpened = cv2.filter2D(img, -1, kernel)
        cv2.imwrite(processed_path, sharpened)

    else:
        return jsonify({"error": "Invalid effect selected"}), 400

    return jsonify({"processed_image": f"/processed/{file.filename}"}), 200

@app.route("/processed/<filename>")
def get_processed_image(filename):
    return send_from_directory(PROCESSED_FOLDER, filename)

if __name__ == "__main__":
    app.run(debug=True)
