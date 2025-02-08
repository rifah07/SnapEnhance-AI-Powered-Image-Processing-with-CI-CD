from flask import Flask, request, send_from_directory, jsonify
from pymongo import MongoClient
import datetime
from dotenv import load_dotenv
import os
import numpy as np
import cv2
import tensorflow as tf
from PIL import Image
from flask_cors import CORS
#from tensorflow.keras.models import load_model
#from tensorflow.keras.preprocessing.image import img_to_array, load_img
from rembg import remove  # Background removal

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)
CORS(app)  #enable CORS for frontend access

# Connection MongoDb
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.snapenhance
collection = db.image_metadata

UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

#load AI Sketch Model
#model = load_model('models/sketch_model.keras')

@app.route("/")
def home():
    return jsonify({"message": "SnapEnhance API with AI & Filters is running!"})

@app.route("/upload", methods=["POST"])
def upload_image():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    file = request.files["image"]
    effect = request.form.get("effect", "sketch")  # Default effect is "sketch"

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)
    
    #saving image data in MongoDb
    def save_image_data(filename):
        image_data = {
            "filename": filename,
            "upload_time": datetime.datetime.now(datetime.timezone.utc),
            "status": "Uploaded"
        }
        db.images.insert_one(image_data)   


    processed_path = os.path.join(PROCESSED_FOLDER, file.filename)

    # Load image & get original size
    img = cv2.imread(file_path)
    original_size = (img.shape[1], img.shape[0])  # (width, height)

    # ✅ Apply selected effect
   # if effect == "sketch":
      # img_pil = Image.open(file_path).convert("RGB")
      # img_pil = img_pil.resize((256, 256))  # Model input size
      # img_array = np.array(img_pil) / 255.0
      # img_array = np.expand_dims(img_array, axis=0)
      #  sketch_output = model.predict(img_array)[0]
      #  sketch_output = (sketch_output * 255).astype(np.uint8)
      #  sketch_output = cv2.resize(sketch_output, original_size)  # Restore original size
      #  processed_image= sketch_output
      #  cv2.imwrite(processed_path, sketch_output)   

    if effect == "grayscale":
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, original_size)  # Restore size
        processed_image= gray
        cv2.imwrite(processed_path, gray)

    elif effect == "invert":
        inverted = cv2.bitwise_not(img)
        inverted = cv2.resize(inverted, original_size)  # Restore size
        processed_image= inverted
        cv2.imwrite(processed_path, inverted)

    elif effect == "blur":
        blurred = cv2.GaussianBlur(img, (15, 15), 0)
        blurred = cv2.resize(blurred, original_size)  # Restore size
        processed_image= blurred
        cv2.imwrite(processed_path, blurred)

    elif effect == "edge-detect":
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        edges = cv2.resize(edges, original_size)  # Restore size
        processed_image= edges
        cv2.imwrite(processed_path, edges)

    elif effect == "background-remove":
        img_pil = Image.open(file_path)
        img_no_bg = remove(img_pil)
        img_no_bg = img_no_bg.resize(original_size)  # Restore size
        processed_image= img_no_bg
        img_no_bg.save(processed_path, "PNG")

    elif effect == "pencil-sketch":
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        inv = cv2.bitwise_not(gray)
        blur = cv2.GaussianBlur(inv, (21, 21), 0)
        sketch = cv2.divide(gray, 255 - blur, scale=256)
        sketch = cv2.resize(sketch, original_size)  # Restore size
        processed_image= sketch
        cv2.imwrite(processed_path, sketch)

    elif effect == "cartoonify":
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.medianBlur(gray, 5)
        edges = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
        color = cv2.bilateralFilter(img, 9, 300, 300)
        cartoon = cv2.bitwise_and(color, color, mask=edges)
        cartoon = cv2.resize(cartoon, original_size)  # Restore size
        processed_image= cartoon
        cv2.imwrite(processed_path, cartoon)

    elif effect == "sharpen":
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        sharpened = cv2.filter2D(img, -1, kernel)
        sharpened = cv2.resize(sharpened, original_size)  # Restore size
        processed_image= sharpened
        cv2.imwrite(processed_path, sharpened)

    else:
        return jsonify({"error": "Invalid effect selected"}), 400
    
   

    filename, ext = os.path.splitext(file.filename)

    #generate new filename with effect name
    output_filename = f"{filename}_{effect}{ext}"
    processed_path = os.path.join(PROCESSED_FOLDER, output_filename)

    # Save processed image with the new filename
    cv2.imwrite(processed_path, processed_image)  

    return jsonify({"processed_image": f"/processed/{output_filename}"}), 200



@app.route("/processed/<filename>")
def get_processed_image(filename):
    return send_from_directory(PROCESSED_FOLDER, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

