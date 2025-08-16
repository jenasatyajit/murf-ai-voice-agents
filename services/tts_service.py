import os
import requests

MURF_API_URL = os.getenv("MURF_API_URL")
MURF_API_KEY = os.getenv("MURF_API_KEY")

if not MURF_API_URL or not MURF_API_KEY:
    raise RuntimeError("MURF_API_URL or MURF_API_KEY not set in environment")

VOICE_ID = "en-US-natalie"
MURF_CHAR_LIMIT = 3000      

def synthesize_speech(text: str) -> str:
    """
    Calls Murf TTS and returns the audio file URL.
    Splits or truncates text to fit.
    """
    tts_text = text[:MURF_CHAR_LIMIT]
    payload = {
        "text": tts_text,
        "voice_id": VOICE_ID
    }
    headers = {
        "api-key": MURF_API_KEY,
        "content-type": "application/json"
    }
    resp = requests.post(MURF_API_URL, json=payload, headers=headers, timeout=60)
    if resp.status_code != 200:
        raise RuntimeError(f"Murf TTS error: {resp.status_code} {resp.text}")
    data = resp.json()
    audio_url = data.get("audioFile")
    if not audio_url:
        raise RuntimeError("Murf TTS returned no audioFile URL")
    return audio_url
