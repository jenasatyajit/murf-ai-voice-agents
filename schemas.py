from pydantic import BaseModel
from typing import Optional

class ChatResponse(BaseModel):
    transcription: str
    llm_response: str
    audioUrl: str
    error: Optional[str] = None
