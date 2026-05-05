import os
from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import uvicorn

# Chargement des variables d'environnement (.env)
load_dotenv()

app = FastAPI(
    title="IA Sponsor for 12 steps programs",
    description="Assistant de soutien basé sur les programmes en 12 étapes"
)

# Configuration pour servir les fichiers statiques et templates
# Assure-toi d'avoir un dossier 'static' et 'templates' si tu sépares les fichiers
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat_endpoint(message: str = Form(...)):
    # Ici, tu insères ta logique OpenAI/Gemini
    # Pour l'exemple, on renvoie une réponse simple
    reply = f"En tant que sponsor, je t'écoute. Tu as dit : {message}"
    return JSONResponse(content={"reply": reply})

@app.post("/voice-chat")
async def voice_chat_endpoint(file: UploadFile = File(...)):
    # Cette route nécessite absolument 'python-multipart'
    return JSONResponse(content={"message": "Fichier audio reçu avec succès"})

if __name__ == "__main__":
    # Render utilise la variable d'environnement PORT (souvent 10000)
    port = int(os.environ.get("PORT", 10000))
    print(f"Démarrage de l'IA Sponsor sur le port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)