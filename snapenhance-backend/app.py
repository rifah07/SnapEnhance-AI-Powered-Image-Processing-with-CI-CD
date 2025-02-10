from flask import Flask, request, send_from_directory, jsonify, Response
from pymongo import MongoClient
import gridfs
import datetime
from dotenv import load_dotenv
import os
import numpy as np
import cv2
from PIL import Image
from flask_cors import CORS
from rembg import remove
import io
from bson import ObjectId 

#load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

#connect to MongoDB
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.snapenhance
collection = db.image_metadata
fs = gridfs.GridFS(db)  # GridFS instance for storing images

UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return jsonify({"message": "SnapEnhance API with AI & Filters is running!"})

@app.route("/upload", methods=["POST"])
def upload_image():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    file = request.files["image"]
    effect = request.form.get("effect", "grayscale")  

    # Save original image locally
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    #save uploaded image metadata in MongoDB
    db.image_metadata.insert_one({
        "filename": file.filename,
        "upload_time": datetime.datetime.now(datetime.timezone.utc),
        "status": "Uploaded"
    })

    processed_path = os.path.join(PROCESSED_FOLDER, file.filename)

    #load image & get original size
    img = cv2.imread(file_path)
    original_size = (img.shape[1], img.shape[0])  # (width, height)

    #apply Effect
    processed_image = None
    if effect == "grayscale":
        processed_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    elif effect == "invert":
        processed_image = cv2.bitwise_not(img)
    elif effect == "blur":
        processed_image = cv2.GaussianBlur(img, (15, 15), 0)
    elif effect == "edge-detect":
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        processed_image = cv2.Canny(gray, 100, 200)
    elif effect == "background-remove":
        img_pil = Image.open(file_path).convert("RGBA")  #ensure RGBA mode
        processed_image = remove(img_pil).resize(original_size)
    elif effect == "pencil-sketch":
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        inv = cv2.bitwise_not(gray)
        blur = cv2.GaussianBlur(inv, (21, 21), 0)
        processed_image = cv2.divide(gray, 255 - blur, scale=256)
    elif effect == "cartoonify":
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.medianBlur(gray, 5)
        edges = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
        color = cv2.bilateralFilter(img, 9, 300, 300)
        processed_image = cv2.bitwise_and(color, color, mask=edges)
    elif effect == "sharpen":
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        processed_image = cv2.filter2D(img, -1, kernel)
    else:
        return jsonify({"error": "Invalid effect selected"}), 400
    
    #generate new filename with effect name
    filename, ext = os.path.splitext(file.filename)
    output_filename = f"{filename}_{effect}.png"
    processed_path = os.path.join(PROCESSED_FOLDER, output_filename)

    #save processed image locally
    if effect == "background-remove":
        processed_image.save(processed_path, "PNG")
    else:
        cv2.imwrite(processed_path, processed_image)

    #convert image to bytes for MongoDB storage
    image_bytes = io.BytesIO()
    if effect == "background-remove":
        processed_image.save(image_bytes, format="PNG")
    else:
        _, buffer = cv2.imencode(".png", processed_image)
        image_bytes.write(buffer)

    image_bytes.seek(0)  # Move to the start of the file

    #save processed image in MongoDB GridFS
    image_id = fs.put(image_bytes, filename=output_filename, metadata={"effect": effect})

    # update MongoDB with processed image metadata
    db.image_metadata.insert_one({
        "filename": output_filename,
        "upload_time": datetime.datetime.now(datetime.timezone.utc),
        "status": "Processed",
        "effect": effect,
        "image_id": str(image_id)
    })

    return jsonify({"processed_image": f"/processed/{output_filename}", "image_id": str(image_id)}), 200

# fixed Route to Get Image from MongoDB GridFS
@app.route("/processed/<image_id>")
def get_processed_image(image_id):
    try:
        image_file = fs.get(ObjectId(image_id))  # Convert string ID to ObjectId
        return Response(image_file.read(), mimetype="image/png")
    except Exception as e:
        return jsonify({"error": f"Image not found: {str(e)}"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)