from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow frontend localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    text: str

@app.post("/chat")
def chat_ai(msg: Message):
    # Later this will be replaced with AI model output
    return {"reply": f"AI: You said '{msg.text}'. Can you tell me more?"}
