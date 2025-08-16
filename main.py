import io
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from data import db_utils
from schemas import ChatResponse
from services.stt_service import transcribe_audio
from services.llm_service import build_prompt, generate_reply
from services.tts_service import synthesize_speech

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

load_dotenv()
MURF_API_URL = os.getenv("MURF_API_URL")
MURF_API_KEY = os.getenv("MURF_API_KEY")
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Init DB
db_utils.init_db()

FALLBACK_AUDIO='/static/fallback.wav'

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the conversational bot UI"""
    with open("static/bot.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.post("/agent/chat/{session_id}", response_model=ChatResponse)
async def agent_chat(session_id: str, file: UploadFile = File(...)):
    """Main conversational bot endpoint"""

    try:
        audio_bytes = await file.read()
        audio_stream = io.BytesIO(audio_bytes)
    except Exception as e:
        return ChatResponse(
            transcription="",
            llm_response="I'm having trouble connecting right now. Please try again later.",
            audioUrl=FALLBACK_AUDIO,
            error=f"Read audio failed: {str(e)}"
        )

    try:
        user_text = transcribe_audio(audio_stream).strip()
        if not user_text:
            raise HTTPException(status_code=400, detail="No speech detected")
    except Exception as e:
        return ChatResponse(
            transcription="",
            llm_response="I'm having trouble connecting right now.",
            audioUrl=FALLBACK_AUDIO,
            error=f"Read audio failed: {str(e)}"
        )

    db_utils.add_message(session_id, "user", user_text)

    history = db_utils.get_last_messages(session_id, limit=10)
    prompt = build_prompt(history, user_text)

    try:
        llm_text = generate_reply(prompt)
        if not llm_text:
            raise HTTPException(status_code=500, detail="LLM returned empty response")
    except Exception as e:
        return ChatResponse(
            transcription=user_text,
            llm_response="I'm having trouble connecting right now. Please try again later.",
            audioUrl=FALLBACK_AUDIO,
            error=f"LLM failed: {str(e)}"
        )

    db_utils.add_message(session_id, "assistant", llm_text)

    try:
        audio_url = synthesize_speech(llm_text)
    except Exception as e:
        return ChatResponse(
            transcription=user_text,
            llm_response="I'm having trouble connecting right now. Please try again later.",
            audioUrl=FALLBACK_AUDIO,
            error=f"TTS failed: {str(e)}"
        )

    return ChatResponse(
        transcription=user_text,
        llm_response=llm_text,
        audioUrl=audio_url
    )

    # try:
    #     # Read audio file
    #     audio_bytes = await file.read()
    #     audio_stream = io.BytesIO(audio_bytes)
    #
    #     # Speech-to-Text
    #     try:
    #         aai.settings.api_key = ASSEMBLYAI_API_KEY
    #         transcriber = aai.Transcriber()
    #         transcript = transcriber.transcribe(audio_stream)
    #         user_text = transcript.text.strip()
    #
    #         if not user_text:
    #             raise HTTPException(status_code=400, detail="No speech detected.")
    #     except Exception as e:
    #         return {
    #             "transcription": "",
    #             "llm_response": "I'm having trouble connecting right now. Please try again later.",
    #             "audioUrl": "/static/fallback.wav",
    #             "error": f"STT failed: {str(e)}"
    #         }
    #
    #     # Save user message
    #     db_utils.add_message(session_id, "user", user_text)
    #
    #     # Get last 10 messages
    #     history = db_utils.get_last_messages(session_id, limit=10)
    #
    #     # Build prompt
    #     history_prompt = "\n".join(f"{role.capitalize()}: {msg}" for role, msg in history)
    #     prompt = f"""
    #     You are a helpful and friendly AI assistant having a natural conversation with the user.
    #     Continue the conversation in a clear and concise way.
    #     Chat History:
    #     {history_prompt}
    #
    #     User: {user_text}
    #     Assistant:
    #     """
    #
    #     # LLM call
    #     try:
    #         model = genai.GenerativeModel("gemini-2.5-flash")
    #         llm_response = model.generate_content(prompt)
    #         llm_text = llm_response.text.strip()
    #         if not llm_text:
    #             raise HTTPException(status_code=500, detail="LLM returned empty response")
    #     except Exception as e:
    #         return {
    #             "transcription": user_text,
    #             "llm_response": "I'm having trouble connecting right now. Please try again later.",
    #             "audioUrl": "/static/fallback.wav",
    #             "error": f"LLM failed: {str(e)}"
    #         }
    #
    #     # Save AI response
    #     db_utils.add_message(session_id, "assistant", llm_text)
    #
    #     # Text-to-Speech
    #     try:
    #         tts_text = llm_text[:3000]  # Murf limit
    #         murf_payload = {"text": tts_text, "voice_id": "en-US-natalie"}
    #         murf_headers = {"api-key": MURF_API_KEY, "content-type": "application/json"}
    #         murf_resp = requests.post(MURF_API_URL, json=murf_payload, headers=murf_headers)
    #         if murf_resp.status_code != 200:
    #             raise HTTPException(status_code=500, detail=f"TTS API error: {murf_resp.text}")
    #         audio_url = murf_resp.json().get("audioFile")
    #     except Exception as e:
    #         return {
    #             "transcription": user_text,
    #             "llm_response": "I'm having trouble connecting right now. Please try again later.",
    #             "audioUrl": "/static/fallback.wav",
    #             "error": f"TTS failed: {str(e)}"
    #         }
    #
    #     return {
    #         "transcription": user_text,
    #         "llm_response": llm_text,
    #         "audioUrl": audio_url
    #     }
    #
    # except Exception as e:
    #     return {
    #         "transcription": "",
    #         "llm_response": "I'm having trouble connecting right now. Please try again later.",
    #         "audioUrl": "/static/fallback.wav",
    #         "error": f"Unexpected Error: {str(e)}"
    #     }
