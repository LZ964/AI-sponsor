import os
import uuid
import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

# Charger les variables d'environnement (.env en local, variables Render en prod)
load_dotenv()

app = FastAPI()

# Configuration CORS pour permettre au navigateur de communiquer avec l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialisation du client OpenAI
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Dossier temporaire pour l'audio (Render utilise /tmp pour l'écriture)
AUDIO_DIR = "/tmp/audio_responses"
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

class ChatRequest(BaseModel):
    message: str

SYSTEM_PROMPT = "Tu es un parrain bienveillant. Sois chaleureux et encourageant."

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = os.path.join(os.getcwd(), "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse(content="<h1>Erreur : index.html non trouvé</h1>", status_code=404)

@app.post("/chat")
async def chat_text(request: ChatRequest):
    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": request.message}
            ]
        )
        return {"response": completion.choices[0].message.content}
    except Exception as e:
        print(f"Erreur Chat: {e}")
        return {"response": "Désolé, je rencontre une petite difficulté technique."}

@app.post("/voice-chat")
async def chat_voice(file: UploadFile = File(...)):
    try:
        temp_id = str(uuid.uuid4())
        input_path = os.path.join(AUDIO_DIR, f"{temp_id}.webm")
        
        # Sauvegarde du fichier audio reçu
        contents = await file.read()
        with open(input_path, "wb") as f:
            f.write(contents)

        # Transcription avec Whisper
        with open(input_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
        
        # Réponse texte de l'IA
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": transcript.text}
            ]
        )
        
        # Synthèse vocale (TTS)
        output_filename = f"{temp_id}.mp3"
        output_path = os.path.join(AUDIO_DIR, output_filename)
        response_audio = client.audio.speech.create(
            model="tts-1-hd",
            voice="fable",
            input=completion.choices[0].message.content
        )
        response_audio.stream_to_file(output_path)

        return {
            "transcript": transcript.text,
            "response": completion.choices[0].message.content,
            "audio_url": f"/audio/{output_filename}"
        }
    except Exception as e:
        print(f"Erreur Voice: {e}")
        return {"transcript": "Erreur", "response": str(e), "audio_url": None}

@app.get("/audio/{filename}")
async def get_audio(filename: str):
    return FileResponse(os.path.join(AUDIO_DIR, filename))

if __name__ == "__main__":
    # Récupération du port dynamique de Render
    port = int(os.environ.get("PORT", 10000))
    print(f"Démarrage sur le port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)