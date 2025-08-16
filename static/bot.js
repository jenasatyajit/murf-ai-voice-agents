console.log("--- bot.js loaded ---");

// Elements
const recordBtn = document.getElementById("recordBtn");
const botAudio = document.getElementById("botAudio");
const chatBox = document.getElementById("chatBox");
const statusBar = document.getElementById("status");

let mediaRecorder;
let audioChunks = [];
let isRecording = false;
let sessionId = new URLSearchParams(window.location.search).get("session_id");

if (!sessionId) {
    sessionId = Math.random().toString(36).substring(2, 10);
    console.log("Generated new session ID:", sessionId);
}

// Toggle Recording
recordBtn.addEventListener("click", async () => {
    if (!isRecording) {
        startRecording();
    } else {
        stopRecording();
    }
});

async function startRecording() {
    console.log("🎤 Start recording");
    try {
        audioChunks = [];
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/webm" });

        mediaRecorder.ondataavailable = (event) => {
            console.log(`📦 Audio chunk: ${event.data.size} bytes`);
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = async () => {
            console.log("🛑 Recording stopped");
            const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
            console.log(`📄 Blob created: ${audioBlob.size} bytes`);
            await sendAudioToServer(audioBlob);
            stream.getTracks().forEach(track => track.stop());
            console.log("🔇 Mic stopped");
        };

        mediaRecorder.start();
        isRecording = true;
        updateUIForRecording(true);

    } catch (err) {
        console.error("❌ Mic access error:", err);
        updateStatus("Microphone access denied ❌");
    }
}

function stopRecording() {
    console.log("🛑 Stop button clicked");
    if (mediaRecorder && mediaRecorder.state === "recording") {
        mediaRecorder.stop();
    }
    isRecording = false;
    updateUIForRecording(false);
    updateStatus("Processing audio...");
}

async function sendAudioToServer(audioBlob) {
    try {
        console.log(`📤 Sending to /agent/chat/${sessionId}...`);
        updateStatus("Sending audio to server...");

        const formData = new FormData();
        formData.append("file", audioBlob, "user_audio.wav");

        const resp = await fetch(`/agent/chat/${sessionId}`, {
            method: "POST",
            body: formData
        });

        const data = await resp.json();
        console.log("✅ Server response:", data);

        if (!resp.ok) {
            console.warn("⚠️ Server returned error:", data);
            appendMessage("(System) I'm having trouble connecting right now.", "bot");
            playFallbackAudio();
            return;
        }

        if (data.transcription) {
            appendMessage(data.transcription, "user");
        }
        if (data.llm_response) {
            appendMessage(data.llm_response, "bot");
        }

        if (data.audioUrl) {
            botAudio.src = data.audioUrl;
            await botAudio.play().catch(err => console.warn("Autoplay blocked:", err));
            console.log("🔊 Bot audio playing");
        }

        updateStatus("✅ Response received");
    } catch (err) {
        console.error("❌ Error sending audio:", err);
        updateStatus(`Error: ${err.message}`);
        appendMessage("(System) Something went wrong.", "bot");
        playFallbackAudio();
    }
}

// Append chat message
function appendMessage(text, sender) {
    const msg = document.createElement("div");
    msg.className = `p-2 rounded max-w-[80%] ${sender === "user" ? "bg-blue-100 self-end" : "bg-gray-200 self-start"}`;
    msg.textContent = text;
    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function updateStatus(text) {
    if (statusBar) statusBar.textContent = text;
}

function playFallbackAudio() {
    botAudio.src = "/static/fallback.wav";
    botAudio.play().catch(err => console.warn("Autoplay blocked:", err));
}

function updateUIForRecording(recording) {
    if (recording) {
        recordBtn.textContent = "⏹ Stop Recording";
        recordBtn.classList.remove("bg-green-500", "hover:bg-green-600");
        recordBtn.classList.add("bg-red-500", "hover:bg-red-600", "animate-pulse");
        updateStatus("Recording... 🎙");
    } else {
        recordBtn.textContent = "🎙 Start Recording";
        recordBtn.classList.remove("bg-red-500", "hover:bg-red-600", "animate-pulse");
        recordBtn.classList.add("bg-green-500", "hover:bg-green-600");
    }
}
