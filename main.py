import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Diagnostic de la clé API
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("ERREUR CRITIQUE : La variable OPENAI_API_KEY est absente !")
else:
    print(f"Clé API détectée (début) : {api_key[:5]}...")

client = OpenAI(api_key=api_key)

@app.get("/")
async def serve_index():
    path = os.path.join(os.getcwd(), "index.html")
    if os.path.exists(path):
        return FileResponse(path)
    return {"error": "index.html non trouvé à la racine"}

# ... garde tes autres routes ici ...

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Démarrage du serveur sur le port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)