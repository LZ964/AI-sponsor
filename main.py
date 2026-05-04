import os
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import uuid

load_dotenv()

app = FastAPI(title="AI Sponsor - 12 Steps Program")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ChatRequest(BaseModel):
    message: str

# Dossier temporaire pour les réponses vocales
if not os.path.exists("audio_responses"):
    os.makedirs("audio_responses")

SYSTEM_PROMPT = (
    "Tu es un parrain (Sponsor) virtuel pour un programme en 12 étapes. "
    "Ton ton est empathique, calme et encourageant. Tu privilégies la communication vocale. "
    "Tu encourages l'utilisateur à t'appeler une fois par jour pour raconter sa journée. "
    "Reste focalisé sur le rétablissement et les principes de sobriété."
)

@app.post("/chat")
async def chat_text(request: ChatRequest):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": request.message}
            ]
        )
        return {"response": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/voice-chat")
async def chat_voice(file: UploadFile = File(...)):
    try:
        # 1. Sauvegarder l'audio reçu temporairement
        temp_filename = f"temp_{uuid.uuid4()}.webm"
        with open(temp_filename, "wb") as buffer:
            buffer.write(await file.read())

        # 2. Transcrire l'audio avec Whisper
        with open(temp_filename, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            )
        os.remove(temp_filename)

        # 3. Obtenir la réponse texte de l'IA
        ai_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": transcript.text}
            ]
        )
        text_output = ai_response.choices[0].message.content

        # 4. Convertir la réponse texte en audio (TTS)
        speech_file_path = f"audio_responses/{uuid.uuid4()}.mp3"
        response_audio = client.audio.speech.create(
            model="tts-1",
            voice="onyx", # Voix calme et mature
            input=text_output
        )
        response_audio.stream_to_file(speech_file_path)

        return {
            "transcript": transcript.text,
            "response_text": text_output,
            "audio_url": f"/audio/{os.path.basename(speech_file_path)}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/audio/{filename}")
async def get_audio(filename: str):
    return FileResponse(f"audio_responses/{filename}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
