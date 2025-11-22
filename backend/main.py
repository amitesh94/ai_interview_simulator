from fastapi import FastAPI, Depends, HTTPException, Header, File, UploadFile
from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal
import models, schemas
from utils import hash_password, verify_password
from auth import create_access_token, verify_token
from ai_service import ask_ai
from schemas import Message
from fastapi.middleware.cors import CORSMiddleware
from schemas import EvalRequest
import os
import uuid
import shutil
import whisper
import edge_tts

# ============================================================
# INITIAL SETUP
# ============================================================
user_interview_state = {}
Base.metadata.create_all(bind=engine)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI()

from fastapi.staticfiles import StaticFiles
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

print("🔊 Loading Whisper model (base)... This happens only once.")
whisper_model = whisper.load_model("base")
print("✅ Whisper model loaded successfully!")


# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# DATABASE SESSION
# ============================================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================
# AUTH HELPERS
# ============================================================
def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return payload


# ============================================================
# AUTH ROUTES
# ============================================================
@app.post("/register")
def register_user(data: schemas.UserCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = hash_password(data.password)
    new_user = models.User(email=data.email, password=hashed)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully"}


@app.post("/login")
def login(data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()

    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid Credentials")

    token = create_access_token({"email": user.email})

    return {"access_token": token, "token_type": "bearer"}


# ============================================================
# PROTECTED TEST ROUTE
# ============================================================
@app.get("/protected")
def protected_route(user=Depends(get_current_user)):
    return {"message": "Success!", "user": user}


# ============================================================
# CHAT (AI RESPONSE)
# ============================================================
@app.post("/chat")
def chat_endpoint(message: Message, user=Depends(get_current_user)):
    ai_reply = ask_ai(message.text)
    return {"reply": ai_reply}


# ============================================================
# VIDEO / AUDIO UPLOAD
# ============================================================
@app.post("/upload_video")
async def upload_video(file: UploadFile = File(...), user=Depends(get_current_user)):

    try:
        ext = file.filename.split(".")[-1]
        filename = f"{uuid.uuid4().hex}.{ext}"

        save_path = os.path.join(UPLOAD_DIR, filename)

        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {"status": "success", "filename": filename}

    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================================
# OFFLINE WHISPER TRANSCRIPTION
# ============================================================
@app.post("/transcribe")
def transcribe_endpoint(filename: str, user=Depends(get_current_user)):

    file_path = os.path.join(UPLOAD_DIR, filename)

    print("\n===================== TRANSCRIPTION REQUEST =====================")
    print(f"🎧 File: {file_path}")

    if not os.path.exists(file_path):
        msg = f"File not found: {file_path}"
        print("❌", msg)
        return {"error": msg}

    try:
        print("🔄 Running Whisper on original file...")

        # Direct transcription (supports .webm directly)
        result = whisper_model.transcribe(file_path)

        text = result.get("text", "").strip()

        if not text:
            return {"error": "Whisper returned empty transcription"}

        print("✅ Transcription Done")
        print("📝 Preview:", text[:100])
        print("=================================================================\n")

        return {"text": text}

    except Exception as e:
        err = str(e)
        print("❌ Whisper Error:", err)
        return {"error": f"Transcription error: {err}"}



@app.get("/ask")
async def ask_question(user=Depends(get_current_user)):
    email = user["email"]

    # Initialize conversation if user not present
    if email not in user_interview_state:
        user_interview_state[email] = {
            "history": []
        }

    history = user_interview_state[email]["history"]

    # AI Prompt for generating next interview question
    prompt = f"""
    You are a professional job interviewer.
    Based on the previous interview history below,
    generate ONLY ONE next interview question.

    Interview History:
    {history}

    Rules:
    - Do NOT repeat any question.
    - Make the next question logical and progressive.
    - Ask common HR and behavioral questions.
    - The response MUST be ONLY a question.
    """

    # Ask AI to generate the next question
    question = ask_ai(prompt).strip()

    # Store in conversation
    history.append({"question": question})

    # Generate audio using TTS
    filename = f"{uuid.uuid4().hex}.mp3"
    filepath = os.path.join(UPLOAD_DIR, filename)

    communicate = edge_tts.Communicate(question, "en-US-GuyNeural")
    await communicate.save(filepath)

    return {"question": question, "audio": filename}

@app.post("/evaluate")
def evaluate_answer(data: EvalRequest, user=Depends(get_current_user)):
    email = user["email"]
    text = data.text

    # Ensure user conversation exists
    if email not in user_interview_state:
        user_interview_state[email] = { "history": [] }

    # Add answer to history
    user_interview_state[email]["history"].append({"answer": text})

    prompt = f"""
    You are evaluating a job interview answer.
    Provide detailed structured feedback with:

    - Communication Score (1–10)
    - Clarity Score (1–10)
    - Confidence Score (1–10)
    - Professionalism Score (1–10)
    - Summary
    - One improvement suggestion

    Answer:
    {text}
    """

    result = ask_ai(prompt)

    return {"evaluation": result}