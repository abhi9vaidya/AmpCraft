# 🎸 AmpCraft

Craft your perfect guitar tone with AI.

## Features
- Upload a guitar audio file
- AI-powered tone analysis (spectral centroid & zero-crossing rate)
- Auto-generates amp, gain, EQ & effects preset

## Project Structure

```
ampcraft/
├── backend/
│   ├── main.py            # API routes (FastAPI)
│   ├── tone_engine.py     # AI tone logic
│   ├── requirements.txt   # Python dependencies
│   └── uploads/           # Uploaded audio files
└── frontend/              # Vite + React UI
```

## Setup & Run

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## API

| Method | Endpoint   | Description                        |
|--------|------------|------------------------------------|
| GET    | `/`        | Health check                       |
| POST   | `/analyze` | Upload audio → returns tone preset |