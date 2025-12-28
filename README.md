# 🎨 Poly Art Generator (Python)

A Python-based tool that converts any input image into **low-poly (polygonal) art** using computational geometry and image processing techniques. The project reconstructs standard images into stylized polygon meshes commonly used in digital art, posters, NFTs, and creative coding.

---

## 🚀 Key Outcomes

- Converts images into **low-poly artwork**
- Geometry-driven (not filter-based)
- Customizable polygon density
- Lightweight and offline
- Reproducible and extensible

---

## 🧠 How It Works

1. **Image Preprocessing**  
   Input image is resized and prepared for efficient processing.

2. **Point Sampling**  
   Strategic points are sampled across the image.

3. **Delaunay Triangulation**  
   Sampled points are triangulated to form polygon meshes.

4. **Color Mapping**  
   Each triangle is filled using the average color of the corresponding region.

5. **Rendering**  
   The final low-poly image is generated and saved.

---

## 🛠️ Tech Stack

- **Language:** Python 3.x  
- **Libraries:**
  - OpenCV
  - NumPy
  - SciPy
  - Pillow / Matplotlib

---

## 📂 Project Structure

poly-art-generator/
│
├── poly_art.py
├── input/
├── output/
├── requirements.txt
└── README.md


---

## ⚙️ Installation

```bash
git clone https://github.com/your-username/poly-art-generator.git
cd poly-art-generator
pip install -r requirements.txt
