import os
import cv2
import pytesseract
from datetime import datetime
from flask import Flask, render_template, request

# ===============================
# PATH TESSERACT
# ===============================
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ===============================
# FLASK CONFIG
# ===============================
app = Flask(__name__)
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.isdir(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ===============================
# IMAGE PREPROCESSING
# ===============================
def preprocess_image(path):
    img = cv2.imread(path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(
        gray, 0, 255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )[1]
    return thresh

# ===============================
# OCR PROCESS
# ===============================
def proses_ocr(path):
    img = preprocess_image(path)
    text = pytesseract.image_to_string(
        img,
        lang="ind",
        config="--oem 1 --psm 6"
    )
    return text.strip()

# ===============================
# ROUTES
# ===============================
@app.route("/", methods=["GET", "POST"])
def index():
    hasil = ""
    if request.method == "POST":
        if "image" not in request.files:
            return render_template("index.html", hasil="⚠️ File tidak ditemukan")

        file = request.files["image"]
        if file.filename == "":
            return render_template("index.html", hasil="⚠️ File belum dipilih")

        filename = datetime.now().strftime("%Y%m%d%H%M%S_") + file.filename
        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(path)

        hasil = proses_ocr(path)

        with open("hasil_ocr.txt", "a", encoding="utf-8") as f:
            f.write(f"\n--- {datetime.now()} ---\n")
            f.write(hasil + "\n")

    return render_template("index.html", hasil=hasil)

@app.route("/history")
def history():
    if os.path.exists("hasil_ocr.txt"):
        with open("hasil_ocr.txt", "r", encoding="utf-8") as f:
            histori = f.read()
    else:
        histori = "Belum ada histori OCR."
    return render_template("history.html", histori=histori)

# ===============================
# RUN
# ===============================
if __name__ == "__main__":
    app.run(debug=True)
