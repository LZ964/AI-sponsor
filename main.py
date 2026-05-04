import os
import uuid
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

app = FastAPI(title="AI Sponsor for 12 steps program")

# Configuration CORS large pour le développement local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialisation OpenAI
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Gestion du dossier audio
AUDIO_DIR = "audio_responses"
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

class ChatRequest(BaseModel):
    message: str

SYSTEM_PROMPT = (
    "Tu es un parrain (Sponsor) virtuel pour une personne suivant un programme en 12 étapes. "
    "Ton ton est bienveillant, calme, empathique mais ferme sur les principes du rétablissement. "
    "Tu préfères la communication vocale. Tu encourages l'utilisateur à te raconter sa journée "
    "au moins une fois par jour pour maintenir sa sobriété."
)

@app.get("/")
def home():
    return {"status": "online", "project": "AI Sponsor"}

@app.post("/chat")
async def chat_text(request: ChatRequest):
    if not api_key:
        raise HTTPException(status_code=500, detail="Clé API OpenAI manquante dans le fichier .env")
    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": request.message}
            ]
        )
        # On s'assure que la clé est bien "response"
        return {"response": completion.choices[0].message.content}
    except Exception as e:
        print(f"Erreur Chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/voice-chat")
async def chat_voice(file: UploadFile = File(...)):
    if not api_key:
        raise HTTPException(status_code=500, detail="Clé API OpenAI manquante")
    try:
        # Sauvegarde temporaire
        temp_id = str(uuid.uuid4())
        input_path = f"{temp_id}_input.webm"
        with open(input_path, "wb") as f:
            f.write(await file.read())

        # Transcription Whisper
        with open(input_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            )
        os.remove(input_path)

        # Réponse GPT
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": transcript.text}
            ]
        )
        text_output = completion.choices[0].message.content

        # Synthèse vocale TTS
        output_filename = f"{temp_id}_out.mp3"
        output_path = os.path.join(AUDIO_DIR, output_filename)
        
        response_audio = client.audio.speech.create(
            model="tts-1",
            voice="onyx",
            input=text_output
        )
        response_audio.stream_to_file(output_path)

        # Retourne les données avec des clés cohérentes
        return {
            "transcript": transcript.text,
            "response": text_output,
            "audio_url": f"/audio/{output_filename}"
        }
    except Exception as e:
        print(f"Erreur Voice-Chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/audio/{filename}")
async def get_audio(filename: str):
    file_path = os.path.join(AUDIO_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Audio non trouvé")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
