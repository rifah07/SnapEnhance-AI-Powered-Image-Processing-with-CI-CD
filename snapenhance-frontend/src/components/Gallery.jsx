import React, { useState } from "react";
import flowerBg from "../assets/flower_bg.jpg";
import "../styles/gallery.css";

const Gallery = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [effect, setEffect] = useState("grayscale");
  const [processedImage, setProcessedImage] = useState(null);
  const [inputImageURL, setInputImageURL] = useState(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setSelectedFile(file);
    setInputImageURL(URL.createObjectURL(file));
    setProcessedImage(null); // Clear previous output when new file is selected
  };

  const handleUpload = async () => {
    if (!selectedFile) return alert("Please select an image!");

    const formData = new FormData();
    formData.append("image", selectedFile);
    formData.append("effect", effect);

    const response = await fetch(
      "https://snapenhance-backend-production.up.railway.app/upload", //Backend API
      {
        method: "POST",
        body: formData,
      }
    );

    const result = await response.json();
    if (response.ok) {
      setProcessedImage(
        `https://snapenhance-backend-production.up.railway.app${result.processed_image}`
      );
    } else {
      alert("Failed to process the image!");
    }
  };

  return (
    <div className="gallery" style={{ backgroundImage: `url(${flowerBg})` }}>
      <div className="upload-container">
        <h2>Upload an Image</h2>
        <input type="file" onChange={handleFileChange} />
        <select value={effect} onChange={(e) => setEffect(e.target.value)}>
          <option value="grayscale">Grayscale</option>
          <option value="invert">Invert</option>
          <option value="blur">Blur</option>
          <option value="edge-detect">Edge Detect</option>
          <option value="pencil-sketch">Pencil Sketch</option>
          <option value="cartoonify">Cartoonify</option>
          <option value="sharpen">Sharpen</option>
        </select>
        <button onClick={handleUpload}>Upload & Apply Effect</button>
      </div>

      {processedImage && (
        <div className="image-container">
          <img src={inputImageURL} alt="Input" className="image" />
          <div className="arrow">↓</div>
          <h2 className="effect-name">
            {effect.replace("-", " ").toUpperCase()}
          </h2>
          <div className="arrow">↓</div>
          <img src={processedImage} alt="Processed" className="image" />
        </div>
      )}
    </div>
  );
};

export default Gallery;
