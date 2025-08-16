import assemblyai as aai
import os
from dotenv import load_dotenv
load_dotenv()

AUDIO_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
if not AUDIO_API_KEY:
    raise RuntimeError("ASSEMBLYAI_API_KEY not set in environment")

aai.settings.api_key = AUDIO_API_KEY

def transcribe_audio(audio_stream) -> str:
    """
    Transcribe audio from a file-like object (BytesIO).
    Returns transcript text.
    Raises on failure.
    """
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_stream)
    return transcript.text or ""
