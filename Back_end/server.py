import io
import os
import json
from PIL import Image
import numpy as np
from typing import List 
from datetime import datetime
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
import google.generativeai as genai
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Database Configuration (Neon)
# DATABASE_URL imported from gemini_api_key_ChechInid.py
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class DetailsDB(Base):
    __tablename__ = "identity_documents"
    id = Column(Integer, primary_key=True, index=True)
    document_number = Column(String(100), index=True)
    full_name = Column(String(100), index=True)
    date_of_birth = Column(Date, index=True)
    gender = Column(String(100), index=True)
    address = Column(String(255), index=True)

Base.metadata.create_all(bind=engine)

def parse_date(date_str):
    """Robustly parse date strings from OCR."""
    if not date_str:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return None

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, '..')

@app.get("/hello")
async def hello():
    return {"message": "Server is running the latest code!"}

# Serve index.html at root
@app.get("/", response_class=HTMLResponse)
async def read_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if not os.path.exists(index_path):
        return HTMLResponse(content=f"Error: index.html not found at {index_path}", status_code=404)
    with open(index_path, "r", encoding="utf-8") as f:
        return f.read()

# Serve app.js
@app.get("/app.js")
async def read_js():
    js_path = os.path.join(STATIC_DIR, "app.js")
    if not os.path.exists(js_path):
        return {"error": f"app.js not found at {js_path}"}
    return FileResponse(js_path)

# Serve style.css
@app.get("/style.css")
async def read_css():
    css_path = os.path.join(STATIC_DIR, "style.css")
    if not os.path.exists(css_path):
        return {"error": f"style.css not found at {css_path}"}
    return FileResponse(css_path)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.post("/file/upload")
async def upload_file(files: List[UploadFile] = File(...)):
    if len(files) < 2:
        return {"status": "error", "message": "Please upload at least 2 images (front and back)."}

    # Process files in pairs or take the first two
    images = []
    processed_filenames = []
    for file in files[:2]:  # Assuming first two are front and back
        contents = await file.read()
        img = Image.open(io.BytesIO(contents)).convert('RGB')
        images.append(img)
        processed_filenames.append(file.filename)

    model = genai.GenerativeModel('gemini-flash-latest')
    
    prompt = """
    Extract the following from these Aadhaar images and return as JSON:
    {
        "full_name": "string",
        "gender": "string",
        "date_of_birth": "YYYY-MM-DD",
        "document_number": "string",
        "address": "string"
    }
    IMPORTANT: Return ONLY the raw JSON object. Use double quotes for keys and string values.
    """

    try:
        response = model.generate_content([prompt] + images)
        text = response.text.replace('```json', '').replace('```', '').strip()
        data = json.loads(text)
        
        db = SessionLocal()
        try:
            new_record = DetailsDB(
                document_number=data.get("document_number"),
                full_name=data.get("full_name"),
                gender=data.get("gender"),
                address=data.get("address"),
                date_of_birth=parse_date(data.get("date_of_birth"))
            )
            db.add(new_record)
            db.commit()
            db.refresh(new_record)
            
            return {
                "status": "success",
                "message": "Data saved to Neon database!",
                "record_id": new_record.id,
                "extracted_data": data,
                "filenames": processed_filenames
            }
        except Exception as e:
            db.rollback()
            return {"status": "error", "message": f"Database error: {str(e)}"}
        finally:
            db.close()
            
    except Exception as e:
        return {"status": "error", "message": f"Gemini/Processing error: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
