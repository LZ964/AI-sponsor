import os
from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import uvicorn

# Chargement des variables d'environnement
load_dotenv()

app = FastAPI(
    title="IA Sponsor for 12 steps programs",
    description="Assistant de soutien basé sur les programmes en 12 étapes"
)

# Configuration du moteur de templates (cherche dans le dossier /templates)
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    """
    Affiche l'interface utilisateur. 
    L'appel est explicite pour éviter les erreurs de type 'tuple' sur certaines versions de Python.
    """
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )

@app.post("/chat")
async def chat_endpoint(message: str = Form(...)):
    """
    Endpoint pour la messagerie texte.
    """
    # Ici, tu pourras intégrer ton appel API OpenAI ou Gemini
    reply = f"Merci pour ton partage. En tant que sponsor, je t'écoute. Tu as dit : {message}"
    return JSONResponse(content={"reply": reply})

@app.post("/voice-chat")
async def voice_chat_endpoint(file: UploadFile = File(...)):
    """
    Endpoint pour les messages vocaux (nécessite python-multipart).
    """
    return JSONResponse(content={"message": "Fichier audio reçu avec succès"})

if __name__ == "__main__":
    # Render utilise la variable d'environnement PORT, par défaut 10000
    port = int(os.environ.get("PORT", 10000))
    print(f"Démarrage de l'IA Sponsor sur le port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)