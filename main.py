import os
import uuid
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AI Sponsor for 12 steps program")

# Autoriser les requêtes CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

AUDIO_DIR = "audio_responses"
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

class ChatRequest(BaseModel):
    message: str

SYSTEM_PROMPT = (
    "Tu es un parrain (Sponsor) virtuel pour une personne suivant un programme en 12 étapes. "
    "Ton ton est empathique et calme. Tu encourages l'utilisateur à te raconter sa journée."
)

# --- ROUTES POUR LE FRONTEND SUR RENDER ---

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    # Envoie le fichier index.html à la racine du site
    return FileResponse("index.html")

# --- ROUTES API ---

@app.post("/chat")
async def chat_text(request: ChatRequest):
    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": request.message}]
        )
        return {"response": completion.choices[0].message.content}
    except Exception as e:
        if "insufficient_quota" in str(e):
            return {"response": "⚠️ Erreur : Plus de crédits sur ton compte OpenAI."}
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/voice-chat")
async def chat_voice(file: UploadFile = File(...)):
    try:
        temp_id = str(uuid.uuid4())
        input_path = f"{temp_id}_in.webm"
        with open(input_path, "wb") as f:
            f.write(await file.read())

        with open(input_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
        os.remove(input_path)

        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": transcript.text}]
        )
        text_output = completion.choices[0].message.content

        output_filename = f"{temp_id}_out.mp3"
        output_path = os.path.join(AUDIO_DIR, output_filename)
        response_audio = client.audio.speech.create(model="tts-1", voice="onyx", input=text_output)
        response_audio.stream_to_file(output_path)

        return {"transcript": transcript.text, "response": text_output, "audio_url": f"/audio/{output_filename}"}
    except Exception as e:
        return {"transcript": "Erreur", "response": f"Erreur API: {str(e)}", "audio_url": None}

@app.get("/audio/{filename}")
async def get_audio(filename: str):
    return FileResponse(os.path.join(AUDIO_DIR, filename))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
