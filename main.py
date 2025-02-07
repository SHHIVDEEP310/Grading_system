from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
import fitz  # PyMuPDF for PDF text extraction
import os
import logging
import sqlite3
from tempfile import NamedTemporaryFile
import pandas as pd
import docx
import hashlib

# Initialize FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging setup
logging.basicConfig(level=logging.DEBUG)

# Database connection
def get_db_connection():
    return sqlite3.connect("grading.db")

# Lifespan event handler (create tables if not exist)
@app.on_event("startup")
async def startup_event():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT,
        score INTEGER,
        total_questions INTEGER
    )
    """)
    conn.commit()
    conn.close()

# Authentication setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
ANSWER_KEY = {}

# Hashing function for passwords
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# Text extraction functions
def extract_text_from_pdf(pdf_path):
    try:
        text = ""
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text("text") + "\n"
        return text.strip()
    except Exception as e:
        logging.error(f"Error extracting text from PDF: {e}")
        return ""

def extract_text_from_docx(docx_path):
    try:
        doc = docx.Document(docx_path)
        return "\n".join([p.text for p in doc.paragraphs])
    except Exception as e:
        logging.error(f"Error extracting text from DOCX: {e}")
        return ""

def extract_text_from_csv(csv_path):
    try:
        df = pd.read_csv(csv_path)
        return "\n".join([f"{row[0]}: {row[1]}" for row in df.values])
    except Exception as e:
        logging.error(f"Error extracting text from CSV: {e}")
        return ""

# Register API
@app.post("/register")
async def register(username: str = Form(...), password: str = Form(...)):
    if len(username) < 4 or len(password) < 6:
        raise HTTPException(status_code=400, detail="Username must be at least 4 characters and password at least 6 characters")

    hashed_password = hash_password(password)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        return {"message": "User registered successfully"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username already exists")
    finally:
        conn.close()

# Login API
@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed_password = hash_password(form_data.password)
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (form_data.username, hashed_password))
    user = cursor.fetchone()
    conn.close()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    return {"access_token": form_data.username, "token_type": "bearer"}

# Upload answer key
@app.post("/upload_answer_key")
async def upload_answer_key(file: UploadFile = File(...)):
    try:
        file_extension = file.filename.split(".")[-1].lower()
        if file_extension not in ["pdf", "txt", "docx", "csv"]:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        temp_file = NamedTemporaryFile(delete=False, suffix=f".{file_extension}")
        temp_file.write(await file.read())
        temp_file.close()

        if file_extension == "pdf":
            extracted_text = extract_text_from_pdf(temp_file.name)
        elif file_extension == "docx":
            extracted_text = extract_text_from_docx(temp_file.name)
        elif file_extension == "csv":
            extracted_text = extract_text_from_csv(temp_file.name)
        else:
            with open(temp_file.name, "r", encoding="utf-8") as f:
                extracted_text = f.read().strip()

        os.remove(temp_file.name)

        global ANSWER_KEY
        ANSWER_KEY = {}
        for line in extracted_text.split("\n"):
            parts = line.split(":")
            if len(parts) == 2:
                key, value = parts[0].strip().lower(), parts[1].strip().lower()
                ANSWER_KEY[key] = value

        return {"message": "Answer key uploaded successfully", "total_questions": len(ANSWER_KEY)}
    
    except Exception as e:
        logging.error(f"Error uploading answer key: {e}")
        raise HTTPException(status_code=500, detail="Error processing the file")

# Process student answers
@app.post("/process_student_answer")
async def process_student_answer(file: UploadFile = File(...), studentName: str = Form(...)):
    try:
        file_extension = file.filename.split(".")[-1].lower()
        temp_file = NamedTemporaryFile(delete=False, suffix=f".{file_extension}")
        temp_file.write(await file.read())
        temp_file.close()

        if file_extension == "pdf":
            extracted_text = extract_text_from_pdf(temp_file.name)
        elif file_extension == "docx":
            extracted_text = extract_text_from_docx(temp_file.name)
        elif file_extension == "csv":
            extracted_text = extract_text_from_csv(temp_file.name)
        else:
            with open(temp_file.name, "r", encoding="utf-8") as f:
                extracted_text = f.read().strip()

        os.remove(temp_file.name)

        extracted_answers = {}
        for line in extracted_text.split("\n"):
            parts = line.split(":")
            if len(parts) == 2:
                extracted_answers[parts[0].strip().lower()] = parts[1].strip().lower()
        
        correct, incorrect, uncertain = 0, 0, 0
        global ANSWER_KEY

        for question, answer in extracted_answers.items():
            if question in ANSWER_KEY:
                if answer == ANSWER_KEY[question]:
                    correct += 1
                else:
                    incorrect += 1
            else:
                uncertain += 1

        total_questions = len(ANSWER_KEY)
        score = (correct / total_questions) * 100 if total_questions > 0 else 0

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO results (student_name, score, total_questions) VALUES (?, ?, ?)", (studentName, score, total_questions))
        conn.commit()
        conn.close()

        return {"student_name": studentName, "score": score, "correct": correct, "incorrect": incorrect, "uncertain": uncertain}
    
    except Exception as e:
        logging.error(f"Error processing student answer: {e}")
        raise HTTPException(status_code=500, detail="Error processing the file")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
