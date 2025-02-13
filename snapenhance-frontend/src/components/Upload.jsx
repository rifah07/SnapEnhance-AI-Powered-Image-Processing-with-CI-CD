import React, { useState } from "react";
import axios from "axios";
import "../styles/gallery.css";

const Upload = () => {
  const [image, setImage] = useState(null);
  const [effect, setEffect] = useState("grayscale");
  const [loading, setLoading] = useState(false);
  const [processedImage, setProcessedImage] = useState("");

  const handleImageChange = (e) => {
    setImage(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!image) {
      alert("Please select an image.");
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append("image", image);
    formData.append("effect", effect);

    try {
      const response = await axios.post(
        `${process.env.REACT_APP_BACKEND_URL}/upload`,
        formData
      );
      setProcessedImage(
        `${process.env.REACT_APP_BACKEND_URL}${response.data.processed_image}`
      );
    } catch (error) {
      console.error("Error uploading image:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-container">
      <h2>Upload an Image</h2>
      <input type="file" onChange={handleImageChange} />
      <select onChange={(e) => setEffect(e.target.value)}>
        <option value="grayscale">Grayscale</option>
        <option value="invert">Invert</option>
        <option value="blur">Blur</option>
        <option value="edge-detect">Edge Detect</option>
        <option value="pencil-sketch">Pencil Sketch</option>
        <option value="cartoonify">Cartoonify</option>
        <option value="sharpen">Sharpen</option>
      </select>
      <button onClick={handleUpload} disabled={loading}>
        {loading ? "Processing..." : "Upload & Apply Effect"}
      </button>

      {processedImage && (
        <div className="preview">
          <h3>Processed Image</h3>
          <img src={processedImage} alt="Processed" />
        </div>
      )}
    </div>
  );
};

export default Upload;
