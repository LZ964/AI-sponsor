import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from openai import OpenAI
from dotenv import load_dotenv
import uvicorn

# Chargement des variables d'environnement
load_dotenv()

# Initialisation du client OpenAI
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

app = FastAPI(title="IA Sponsor for 12 steps programs")

# Configuration du moteur de templates
templates = Jinja2Templates(directory="templates")

# Instructions de rôle pour l'IA
SYSTEM_PROMPT = (
    "Tu es un sponsor bienveillant pour une personne suivant un programme en 12 étapes. "
    "Ton ton est encourageant, honnête et respectueux. Tu connais bien les traditions et les étapes. "
    "Tu dois offrir du soutien, partager de l'espoir et rester focalisé sur le rétablissement."
)

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    """Affiche l'interface utilisateur (index.html dans le dossier templates)"""
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )

@app.post("/chat")
async def chat_endpoint(message: str = Form(...)):
    """Envoie le message à OpenAI et retourne la réponse du sponsor"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message}
            ],
            max_tokens=500
        )
        reply = response.choices[0].message.content
    except Exception as e:
        reply = "Je suis désolé, j'ai une petite difficulté technique pour me connecter. Respire un grand coup, je reviens vite."
        print(f"Erreur OpenAI: {e}")

    return JSONResponse(content={"reply": reply})

if __name__ == "__main__":
    # Port dynamique pour Render
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)