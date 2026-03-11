import os
import secrets
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session as DBSession
from dotenv import load_dotenv
from google import genai
from google.genai import types

import models, schemas
from database import engine, get_db

load_dotenv()

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Chatbot API",
    description="A simple API for an AI chatbot using Google Gemini and SQLite, with multimodal support.",
    version="1.1.0"
)

# Mount static and uploads
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Initialize Gemini Client
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

try:
    if GEMINI_API_KEY:
        ai_client = genai.Client(api_key=GEMINI_API_KEY)
    else:
        ai_client = None
        print("Warning: GEMINI_API_KEY not found in environment variables.")
except Exception as e:
    ai_client = None
    print(f"Error initializing GenAI client: {e}")

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/", include_in_schema=False)
def serve_home():
    return FileResponse("static/index.html")

@app.post("/sessions", response_model=schemas.SessionResponse)
def create_session(request: schemas.SessionCreate, db: DBSession = Depends(get_db)):
    db_session = models.Session(system_prompt=request.system_prompt)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


@app.get("/sessions/{session_id}/history", response_model=schemas.SessionHistoryResponse)
def get_session_history(session_id: int, db: DBSession = Depends(get_db)):
    db_session = db.query(models.Session).filter(models.Session.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_session


@app.post("/sessions/{session_id}/chat", response_model=schemas.MessageResponse)
async def chat_with_ai(
    session_id: int,
    content: str | None = Form(None),
    file: UploadFile | None = File(None),
    db: DBSession = Depends(get_db)
):
    if not ai_client:
        raise HTTPException(status_code=500, detail="AI Client is not initialized.")

    if not content and not file:
        raise HTTPException(status_code=400, detail="Must provide either content or a file.")

    db_session = db.query(models.Session).filter(models.Session.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")

    file_path_db = None
    file_type_db = None
    file_bytes = None

    # Handle file upload saving
    if file:
        file_ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{secrets.token_hex(8)}{file_ext}"
        saved_file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        file_bytes = await file.read()
        with open(saved_file_path, "wb") as f:
            f.write(file_bytes)
            
        file_path_db = saved_file_path
        file_type_db = file.content_type

    # Save user message
    user_msg = models.Message(
        session_id=session_id,
        role="user",
        content=content,
        file_path=file_path_db,
        file_type=file_type_db
    )
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    # Fetch history to build Gemini context array
    history = db.query(models.Message).filter(
        models.Message.session_id == session_id
    ).order_by(models.Message.created_at).all()
    
    genai_contents = []
    for msg in history:
        # We only pass history text to Gemini for standard context to avoid massive payloads,
        # but for the current message, we pass the actual image.
        role = "user" if msg.role == "user" else "model"
        parts = []
        
        if msg.id == user_msg.id and file_bytes and file_type_db:
            # Current message has an image we need to pass
            parts.append(
                 types.Part.from_bytes(data=file_bytes, mime_type=file_type_db)
            )
            
        if msg.content:
            parts.append(types.Part.from_text(text=msg.content))
            
        if parts:
            genai_contents.append({"role": role, "parts": parts})

    try:
        config = None
        if db_session.system_prompt:
            config = types.GenerateContentConfig(
                system_instruction=db_session.system_prompt
            )

        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=genai_contents,
            config=config
        )
        ai_response_text = response.text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating AI response: {str(e)}")

    # Save AI message
    ai_msg = models.Message(session_id=session_id, role="model", content=ai_response_text)
    db.add(ai_msg)
    db.commit()
    db.refresh(ai_msg)

    return ai_msg
