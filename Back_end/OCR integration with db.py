import json
from datetime import datetime
import google.generativeai as genai
import PIL.Image
from gemini_api_key_ChechInid import GEMINI_API_KEY
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.orm import sessionmaker, declarative_base

genai.configure(api_key=GEMINI_API_KEY)


# FIXED: Added "+psycopg2" after postgresql so SQLAlchemy knows which driver to use
DATABASE_URL = 'postgresql+psycopg2://neondb_owner:npg_NRwpjlI2ZLy6@ep-gentle-grass-ahhh2cgz-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require'

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

def extract_text_from_image(front_path, back_path):
    print(f"Loading images: {front_path} and {back_path}")
    try:
        img_front = PIL.Image.open(front_path)
        img_back = PIL.Image.open(back_path)
    except Exception as e:
        print(f"Error loading images: {e}")
        return

    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = """
    Extract the following from these Aadhaar images and return as JSON:
    {
        "full_name": "string",
        "gender": "string",
        "date_of_birth": "YYYY-MM-DD",
        "document_number": "string",
        "address": "string"
    }
    IMPORTANT: Return ONLY the raw JSON object.
    """

    print("Calling Gemini API...")
    try:
        response = model.generate_content([prompt, img_front, img_back])
        text = response.text.replace('```json', '').replace('```', '').strip()
        print("\nExtracted Data:")
        print(text)
        data = json.loads(text)
        return data 
        
    except Exception as e:
        print(f"Error during Gemini inference: {e}")

    return extract_text_from_image(img_front_p, img_back_p)

try:
    front_img = r"C:\Users\Sam\OneDrive\Pictures\trail_card2.jpeg"
    back_img = r"C:\Users\Sam\OneDrive\Pictures\trial_card.jpeg"
    
    data = extract_text_from_image(front_img, back_img)
    db = SessionLocal()
    
    # FIXED: Added robust date parsing to handle '01/04/2003' vs '2003-04-01'
    new_record = DetailsDB(
        document_number=data.get("document_number"),
        full_name=data.get("full_name"),
        gender=data.get("gender"),
        address=data.get("address"),
        date_of_birth=parse_date(data.get("date_of_birth"))
    )
    
    db.add(new_record)
    db.commit()
    print("SUCCESS: Image data saved to Cloud PostgreSQL (Neon)!")
except Exception as e:
    print(f"ERROR: Failed to save data: {str(e)}")
finally:
    if 'db' in locals():
        db.close()


    