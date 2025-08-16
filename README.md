# 🎙️ Murf AI Conversational Bot

An AI-powered conversational voice agent built with **FastAPI**, **AssemblyAI**, **Google Gemini**, and **Murf AI**.  
The bot listens to your voice, transcribes it, generates intelligent responses using an LLM, and speaks back to you in a natural Murf AI voice — all while maintaining chat history.

---

## 📌 Features

- **🎤 Speech-to-Text (STT)** — Uses **AssemblyAI** to transcribe user audio in real-time.
- **🧠 Conversational AI** — Uses **Google Gemini (2.5-flash)** to understand and respond contextually.
- **🔊 Text-to-Speech (TTS)** — Uses **Murf AI** to generate natural-sounding responses.
- **💬 Chat History** — Stores and retrieves past conversation context using **SQLite**.
- **⚠️ Robust Error Handling** — Gracefully handles API failures with fallback pre-generated audio.
- **📱 Clean UI** — TailwindCSS-based interface for easy interaction.

---

## 🛠️ Tech Stack

### **Frontend**
- HTML, TailwindCSS
- Vanilla JavaScript
- Fetch API for communication with backend

### **Backend**
- FastAPI (Python)
- SQLite for chat history
- AssemblyAI SDK for speech-to-text
- Google Gemini API for LLM responses
- Murf AI API for text-to-speech

---

## 🏗️ Architecture

```text
🎤 User Audio
   ↓ (Browser mic)
Frontend (bot.js)
   ↓ POST /agent/chat/{session_id}
FastAPI Backend
   ↓ STT (AssemblyAI)
   ↓ Append to SQLite chat history
   ↓ LLM Response (Google Gemini)
   ↓ Append response to chat history
   ↓ TTS (Murf AI)
   ↓ Return transcription + LLM text + audio URL
Frontend
   ↓ Play bot audio & display chat bubbles
```


---

# 📂 Project Structure

```text
/project-root
│── bot.html              # Conversational bot UI
│── bot.js                # Frontend logic
│── main.py               # FastAPI backend
│── db_utils.py           # SQLite database helpers
│── /data                 # SQLite DB file stored here
│── /static               # Static JS/CSS files
│── README.md             # Project documentation
```

---

# ⚙️ Environment Variables
Before running the project, create a .env file in the root with:

```text
ASSEMBLYAI_API_KEY=your_assemblyai_api_key
GEMINI_API_KEY=your_gemini_api_key
MURF_API_KEY=your_murf_api_key
MURF_API_URL=murf_endpoint_url
```

---

# 🚀 How to Run

### 1️⃣ Clone the repository
```terminaloutput
git clone https://github.com/your-username/murf-ai-bot.git
cd murf-ai-bot
```

### 2️⃣ Install dependencies
It’s recommended to use a virtual environment:
```text
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### 3️⃣ Create .env file
Add your API keys:
```text
ASSEMBLYAI_API_KEY=your_assemblyai_api_key
GEMINI_API_KEY=your_gemini_api_key
MURF_API_KEY=your_murf_api_key
MURF_API_URL=murf_endpoint_url
```

### 4️⃣ Run the FastAPI server
```terminaloutput
uvicorn main:app --reload
```

### 5️⃣ Open in browser
Navigate to: http://localhost:8000/
