from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from tone_engine import generate_chain
from feature_extractor import extract_named
import shutil, os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def _get_tone_class(named: dict) -> str:
    """
    Classify audio into: jazz | clean | blues | rock | high_gain | metal | bass
    Full-band mixes pull centroid down, so ZCR is the primary distortion indicator.
    """
    centroid = named["centroid"]
    zcr      = named["zcr"]
    rms      = named["rms"]
    rolloff  = named.get("rolloff", centroid * 2)

    if rms < 0.015:                             return "bass"
    if zcr > 0.13:                              return "metal"
    if zcr > 0.09 and centroid > 3500:          return "high_gain"
    if zcr > 0.09:                              return "rock"      # high ZCR alone = rock (full band mixes have low centroid)
    if zcr > 0.07 and centroid > 2500:          return "rock"
    if zcr > 0.06 and rolloff > 4000:           return "rock"      # bright rolloff confirms rock even if centroid is mid
    if zcr > 0.04 and centroid > 2000:          return "blues"
    if zcr > 0.06:                              return "blues"     # dark gritty tone — low centroid but ZCR confirms drive
    if centroid < 1800 and zcr < 0.04:          return "jazz"
    return "clean"


@app.get("/")
def home():
    return {"message": "AmpCraft Backend Running 🎸"}


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"filename": file.filename, "message": "File uploaded successfully ✅"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    try:
        file_path = os.path.join(UPLOAD_DIR, os.path.basename(file.filename))
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        named      = extract_named(file_path)
        tone_class = _get_tone_class(named)
        chain      = generate_chain(tone_class, named)

        return {"chain": chain, "features": named}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))