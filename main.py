import io
import os
import uuid
import aiofiles
import assemblyai as aai
import google.generativeai as genai
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from data import db_utils

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

load_dotenv()
MURF_API_URL = os.getenv("MURF_API_URL")
MURF_API_KEY = os.getenv("MURF_API_KEY")
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Init DB
db_utils.init_db()

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not set in .env")

genai.configure(api_key=GEMINI_API_KEY)
os.makedirs("uploads", exist_ok=True)


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the conversational bot UI"""
    with open("static/bot.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.get("/bot", response_class=HTMLResponse)
async def bot_ui():
    """Optional: Keep /bot as an alias for the main bot page"""
    with open("static/bot.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.post("/agent/chat/{session_id}")
async def agent_chat(session_id: str, file: UploadFile = File(...)):
    """Main conversational bot endpoint"""
    try:
        # Read audio file
        audio_bytes = await file.read()
        audio_stream = io.BytesIO(audio_bytes)

        # Speech-to-Text
        try:
            aai.settings.api_key = ASSEMBLYAI_API_KEY
            transcriber = aai.Transcriber()
            transcript = transcriber.transcribe(audio_stream)
            user_text = transcript.text.strip()

            if not user_text:
                raise HTTPException(status_code=400, detail="No speech detected.")
        except Exception as e:
            return {
                "transcription": "",
                "llm_response": "I'm having trouble connecting right now. Please try again later.",
                "audioUrl": "/static/fallback.wav",
                "error": f"STT failed: {str(e)}"
            }

        # Save user message
        db_utils.add_message(session_id, "user", user_text)

        # Get last 10 messages
        history = db_utils.get_last_messages(session_id, limit=10)

        # Build prompt
        history_prompt = "\n".join(f"{role.capitalize()}: {msg}" for role, msg in history)
        prompt = f"""
        You are a helpful and friendly AI assistant having a natural conversation with the user.
        Continue the conversation in a clear and concise way.
        Chat History:
        {history_prompt}

        User: {user_text}
        Assistant:
        """

        # LLM call
        try:
            model = genai.GenerativeModel("gemini-2.5-flash")
            llm_response = model.generate_content(prompt)
            llm_text = llm_response.text.strip()
            if not llm_text:
                raise HTTPException(status_code=500, detail="LLM returned empty response")
        except Exception as e:
            return {
                "transcription": user_text,
                "llm_response": "I'm having trouble connecting right now. Please try again later.",
                "audioUrl": "/static/fallback.wav",
                "error": f"LLM failed: {str(e)}"
            }

        # Save AI response
        db_utils.add_message(session_id, "assistant", llm_text)

        # Text-to-Speech
        try:
            tts_text = llm_text[:3000]  # Murf limit
            murf_payload = {"text": tts_text, "voice_id": "en-US-natalie"}
            murf_headers = {"api-key": MURF_API_KEY, "content-type": "application/json"}
            murf_resp = requests.post(MURF_API_URL, json=murf_payload, headers=murf_headers)
            if murf_resp.status_code != 200:
                raise HTTPException(status_code=500, detail=f"TTS API error: {murf_resp.text}")
            audio_url = murf_resp.json().get("audioFile")
        except Exception as e:
            return {
                "transcription": user_text,
                "llm_response": "I'm having trouble connecting right now. Please try again later.",
                "audioUrl": "/static/fallback.wav",
                "error": f"TTS failed: {str(e)}"
            }

        return {
            "transcription": user_text,
            "llm_response": llm_text,
            "audioUrl": audio_url
        }

    except Exception as e:
        return {
            "transcription": "",
            "llm_response": "I'm having trouble connecting right now. Please try again later.",
            "audioUrl": "/static/fallback.wav",
            "error": f"Unexpected Error: {str(e)}"
        }
