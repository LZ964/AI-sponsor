import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AI Sponsor for 12 steps program")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def home():
    return {"project": "AI Sponsor for 12 steps program", "status": "active"}

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    if not api_key:
        raise HTTPException(status_code=500, detail="Clé API manquante.")
    
    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "Tu es un parrain (Sponsor) virtuel pour une personne suivant un programme en 12 étapes. "
                        "Ton ton est bienveillant, encourageant, mais ferme sur les principes du rétablissement. "
                        "Tu aides l'utilisateur final à réfléchir sur ses étapes et à maintenir sa sobriété au quotidien."
                    )
                },
                {"role": "user", "content": request.message}
            ]
        )
        return {"response": completion.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
