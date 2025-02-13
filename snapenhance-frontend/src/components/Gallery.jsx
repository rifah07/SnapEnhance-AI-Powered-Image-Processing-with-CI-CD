import React, { useState, useEffect } from "react";
//import axios from "axios";
import flowerBg from "../assets/flower_bg.jpg";
import "../styles/gallery.css";

const Gallery = () => {
  const [images, setImages] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [effect, setEffect] = useState("grayscale");

  useEffect(() => {
    fetch("https://snapenhance-backend-production.up.railway.app/processed")
      .then((res) => res.json())
      .then((data) => setImages(data))
      .catch((err) => console.error(err));
  }, []);

  const handleFileChange = (e) => setSelectedFile(e.target.files[0]);

  const handleUpload = async () => {
    if (!selectedFile) return alert("Please select an image!");

    const formData = new FormData();
    formData.append("image", selectedFile);
    formData.append("effect", effect);

    const response = await fetch(
      "https://snapenhance-backend-production.up.railway.app/upload",
      {
        method: "POST",
        body: formData,
      }
    );

    const result = await response.json();
    if (response.ok) setImages([...images, result.processed_image]);
  };

  return (
    <div className="gallery" style={{ backgroundImage: `url(${flowerBg})` }}>
      {/* Upload form */}
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

      {/* Gallery Images */}
      <h1>Gallery</h1>
      {images.length === 0 ? (
        <p>No processed images found.</p>
      ) : (
        <div className="image-grid">
          {images.map((img, index) => (
            <div key={index} className="image-card">
              <img
                src={`https://snapenhance-backend-production.up.railway.app${img}`}
                alt="Processed"
              />
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Gallery;
