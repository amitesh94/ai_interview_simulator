from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal
import models, schemas
from utils import hash_password, verify_password
from auth import create_access_token
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Header, HTTPException
from auth import verify_token
from ai_service import ask_ai
from schemas import Message

# Create all DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency - DB Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# REGISTER API
@app.post("/register")
def register_user(data: schemas.UserCreate, db: Session = Depends(get_db)):
    print("REGISTER PASSWORD:", data.password)
    user = db.query(models.User).filter(models.User.email == data.email).first()
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = hash_password(data.password)
    new_user = models.User(email=data.email, password=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully"}


# LOGIN API
@app.post("/login")
def login(data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid Credentials")

    if not verify_password(data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid Credentials")

    token = create_access_token({"email": user.email})

    return {"access_token": token, "token_type": "bearer"}

def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    token = authorization.replace("Bearer ", "")

    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return payload

@app.get("/protected")
def protected_route(user=Depends(get_current_user)):
    return {"message": "Success!", "user": user}

@app.post("/chat")
def chat_endpoint(message: Message, user=Depends(get_current_user)):
    text = message.text

    # Call AI
    ai_reply = ask_ai(text)

    return {"reply": ai_reply}
