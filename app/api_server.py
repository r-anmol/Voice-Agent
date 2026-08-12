# app/api_server.py

import os
import asyncio
import tempfile
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from openai import AsyncOpenAI
from app.graph import run_kavya_turn  # make sure graph.py is in app/ and app/__init__.py exists

load_dotenv()

# OpenAI client (reads OPENAI_API_KEY from env)
client = AsyncOpenAI()

app = FastAPI(title="Kavya API", version="1.0")

# CORS (Next.js dev server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------
# Models
# -------------------------
class ChatIn(BaseModel):
    user_id: str = "Anmol"
    message: str


class ChatOut(BaseModel):
    reply: str


class TTSIn(BaseModel):
    text: str
    voice: str = "coral"  # keep same as CLI
    # keep it safe + friendly for frontend
    instructions: str = (
        "Speak warmly, friendly, slightly playful, Hindi-English mix. Keep it PG."
    )


# -------------------------
# Helpers
# -------------------------
def _safe_unlink(path: str):
    try:
        os.remove(path)
    except Exception:
        pass


# -------------------------
# Routes
# -------------------------
@app.get("/health")
async def health():
    return {"ok": True}


@app.post("/chat", response_model=ChatOut)
async def chat(payload: ChatIn):
    msg = (payload.message or "").strip()
    if not msg:
        raise HTTPException(status_code=400, detail="message is required")

    # run sync agent without blocking event loop
    try:
        reply = await asyncio.to_thread(run_navya_turn, msg, payload.user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"agent error: {e}")

    return {"reply": reply or ""}


@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    # Accept common browser formats (webm, wav, mp3, m4a, etc.)
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="empty audio file")

    # Write to temp file (most compatible with SDK)
    suffix = ""
    if file.filename and "." in file.filename:
        suffix = "." + file.filename.rsplit(".", 1)[-1]
    if not suffix:
        suffix = ".webm"

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp_path = tmp.name
    try:
        tmp.write(data)
        tmp.flush()
        tmp.close()

        try:
            with open(tmp_path, "rb") as f:
                # STT model
                result = await client.audio.transcriptions.create(
                    model="gpt-4o-mini-transcribe",
                    file=f,
                )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"transcribe error: {e}")

        text = getattr(result, "text", None) or ""
        return {"text": text}

    finally:
        _safe_unlink(tmp_path)


@app.post("/tts")
async def tts(payload: TTSIn, background: BackgroundTasks):
    text = (payload.text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="text is required")

    # Save mp3 to temp and return as file response
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tmp_path = tmp.name
    tmp.close()

    try:
        async with client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice=payload.voice,
            input=text,
            instructions=payload.instructions,
            response_format="mp3",
        ) as response:
            # Stream bytes to file (works reliably with Async client)
            with open(tmp_path, "wb") as f:
                async for chunk in response.iter_bytes():
                    f.write(chunk)

        # Delete after sending
        background.add_task(_safe_unlink, tmp_path)

        return FileResponse(
            tmp_path,
            media_type="audio/mpeg",
            filename="kavya.mp3",
            background=background,
        )

    except HTTPException:
        _safe_unlink(tmp_path)
        raise
    except Exception as e:
        _safe_unlink(tmp_path)
        raise HTTPException(status_code=500, detail=f"tts error: {e}")
