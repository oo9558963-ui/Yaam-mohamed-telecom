import os, requests
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from groq import Groq
app = FastAPI()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
PROMPT = """Tu es Yaam de MOHAMED TELECOM, Bobo-Dioulasso. Tu vends téléphones, unités Orange/Moov/Telecel, accessoires, réparation, chargement. WhatsApp: 65784728 / Appel: 78538931. Accueille par 'Barka ! Bienvenue chez MOHAMED TELECOM 📱'. Demande budget/marque pour téléphone, panne pour réparation. Conclus toujours avec les 2 numéros."""
def ask_groq(t):
    c=client.chat.completions.create(model="openai/gpt-oss-20b",messages=[{"role":"system","content":PROMPT},{"role":"user","content":t}],max_tokens=500)
    return c.choices[0].message.content
@app.get("/")
def home(): return {"status":"MOHAMED TELECOM OK"}
@app.get("/webhook")
def verify(request: Request):
    if request.query_params.get("hub.verify_token")==os.getenv("VERIFY_TOKEN","yaam2024"):
        return PlainTextResponse(request.query_params.get("hub.challenge"))
    return PlainTextResponse("error",403)
@app.post("/webhook")
async def webhook(request: Request):
    data=await request.json()
    if data.get("object")=="page":
        for entry in data.get("entry",[]):
            for ev in entry.get("messaging",[]):
                if "message" in ev and "text" in ev["message"]:
                    reply=ask_groq(ev["message"]["text"])
                    requests.post(f"https://graph.facebook.com/v18.0/me/messages?access_token={os.getenv('PAGE_ACCESS_TOKEN')}",json={"recipient":{"id":ev["sender"]["id"]},"message":{"text":reply}})
    return {"status":"ok"}
