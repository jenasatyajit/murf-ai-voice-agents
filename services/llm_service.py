import os
import google.generativeai as genai
from typing import List, Tuple

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set in environment")

genai.configure(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-2.5-flash" 

def build_prompt(history: List[Tuple[str, str]], user_text: str) -> str:
    """
    history: List of (role, text) where role in {"user","assistant"}
    """
    history_lines = []
    for role, msg in history:
        prefix = "User" if role == "user" else "Assistant"
        history_lines.append(f"{prefix}: {msg}")

    history_block = "\n".join(history_lines)

    system_instructions = (
        "You are a helpful, friendly AI assistant having a natural, concise conversation. "
        "Prefer clear, grounded explanations. If uncertain, ask clarifying questions briefly."
    )

    prompt = (
        f"{system_instructions}\n\n"
        f"Chat History:\n{history_block}\n\n"
        f"User: {user_text}\n"
        f"Assistant:"
    )
    return prompt

def generate_reply(prompt: str) -> str:
    """
    Calls Gemini to generate the assistant reply.
    Returns the response text.
    """
    model = genai.GenerativeModel(MODEL_NAME)
    resp = model.generate_content(prompt)
    return (resp.text or "").strip()
