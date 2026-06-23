"""
Artipen API Server
"""
from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3
from pathlib import Path
from typing import Optional

app = FastAPI(title="Artipen API", version="1.0.0")
DB_PATH = Path.home() / ".artipen" / "artipen.db"

class GenerateRequest(BaseModel):
    prompt: str
    style: str = "default"
    model: str = "sdxl"
    seed: Optional[int] = None

def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

@app.post("/api/v1/generate")
async def generate_image(req: GenerateRequest):
    db = get_db()
    db.execute("INSERT INTO generations (prompt, style, model) VALUES (?, ?, ?)",
               (req.prompt, req.style, req.model))
    db.commit()
    return {"status": "queued", "prediction": {"quality_score": 0.85}}

@app.post("/api/v1/predict/quality")
async def predict_quality(image_path: str):
    return {"prediction": {"aesthetic_score": 7.5, "technical_score": 8.2}}

@app.get("/health")
async def health():
    return {"status": "ok"}
