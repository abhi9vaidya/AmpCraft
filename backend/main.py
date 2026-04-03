from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from tone_engine import generate_chain
import shutil
import os
import librosa
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
def home():
    return {"message": "AmpCraft Backend Running 🎸"}


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {
            "filename": file.filename,
            "message": "File uploaded successfully ✅"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    try:
        # Save file (sanitized to prevent path traversal)
        file_path = os.path.join(UPLOAD_DIR, os.path.basename(file.filename))
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Load audio
        y, sr = librosa.load(file_path)

        # Extract features
        centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
        zcr = np.mean(librosa.feature.zero_crossing_rate(y))

        # Generate signal chain
        chain = generate_chain(float(centroid), float(zcr))

        return {
            "chain": chain,
            "features": {
                "centroid": float(centroid),
                "zcr":      float(zcr)
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))