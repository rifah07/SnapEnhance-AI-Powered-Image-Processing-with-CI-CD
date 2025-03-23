from flask import Flask, request, jsonify, send_from_directory
import os
import numpy as np
import cv2
from PIL import Image
from flask_cors import CORS
from rembg import remove

app = Flask(__name__)
CORS(app)

#create folders if they don’t exist
UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return jsonify({"message": "SnapEnhance API is running!"})

@app.route("/upload", methods=["POST"])
def upload_image():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    file = request.files["image"]
    effect = request.form.get("effect", "grayscale")  

    #save original image locally
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)
    print(f"Image saved at: {file_path}")  # Debugging print

    #load image
    img = cv2.imread(file_path)
    if img is None:
        return jsonify({"error": "Failed to read the uploaded image"}), 500
    
    original_size = (img.shape[1], img.shape[0])  # (width, height)

    #apply effect
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
        img_pil = Image.open(file_path).convert("RGBA")  # Ensure RGBA mode
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
    
    #generate new filename
    filename, ext = os.path.splitext(file.filename)
    output_filename = f"{filename}_{effect}.png"
    processed_path = os.path.join(PROCESSED_FOLDER, output_filename)

    #save processed image
    if effect == "background-remove":
        processed_image.save(processed_path, "PNG")
    else:
        cv2.imwrite(processed_path, processed_image)

    print(f"Processed image saved at: {processed_path}")  #debugging print

    return jsonify({"processed_image": f"/processed/{output_filename}"}), 200

@app.route("/processed/<filename>")
def get_processed_image(filename):
    return send_from_directory(PROCESSED_FOLDER, filename)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)