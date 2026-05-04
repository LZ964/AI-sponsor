import os
import uuid
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# --- CONFIGURATION CRITIQUE POUR RENDER ---
# Autorise le navigateur à communiquer avec le serveur une fois en ligne
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Dossier temporaire compatible avec Render
AUDIO_DIR = "/tmp/audio_responses"
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

class ChatRequest(BaseModel):
    message: str

SYSTEM_PROMPT = (
    "Tu es un parrain virtuel bienveillant. Ton ton est chaleureux, "
    "empathique et encourageant. Utilise une ponctuation expressive."
)

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return HTMLResponse("Erreur : index.html introuvable à la racine.")

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
        return {"response": f"Désolé, j'ai une erreur technique : {str(e)}"}

@app.post("/voice-chat")
async def chat_voice(file: UploadFile = File(...)):
    try:
        temp_id = str(uuid.uuid4())
        input_path = os.path.join(AUDIO_DIR, f"{temp_id}.webm")
        with open(input_path, "wb") as f:
            f.write(await file.read())

        with open(input_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
        
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": transcript.text}
            ]
        )
        text_output = completion.choices[0].message.content

        output_filename = f"{temp_id}.mp3"
        output_path = os.path.join(AUDIO_DIR, output_filename)
        response_audio = client.audio.speech.create(model="tts-1-hd", voice="fable", input=text_output)
        response_audio.stream_to_file(output_path)

        return {
            "transcript": transcript.text,
            "response": text_output,
            "audio_url": f"/audio/{output_filename}"
        }
    except Exception as e:
        print(f"Erreur Voice: {e}")
        return {"transcript": "Erreur", "response": str(e), "audio_url": None}

@app.get("/audio/{filename}")
async def get_audio(filename: str):
    file_path = os.path.join(AUDIO_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404)

# --- LANCEMENT DYNAMIQUE DU PORT ---
if __name__ == "__main__":
    import uvicorn
    # Lit le port imposé par Render ou utilise 8000 par défaut
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)