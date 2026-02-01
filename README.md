# 📚 Project Documentation: CheckInID

This documentation covers all code files in the CheckInID project, explaining their purposes, structure, and how they interact. The project enables users to upload Aadhaar card images via a web interface, extract details using Gemini AI, and store results in a PostgreSQL database. The backend is hosted on Render and the frontend on Netlify.

---

## requirements.txt

This file lists all Python dependencies required for the backend FastAPI server.

```txt
fastapi uvicorn python-dotenv python-multipart google-generativeai sqlalchemy psycopg2-binary pillow numpy
```

### Purpose

- **Dependency Management**: Ensures that all required libraries are installed in the backend environment.
- **Reproducibility**: Anyone deploying or developing can replicate the backend environment exactly.

### Libraries Breakdown

| Package                | Purpose                                                         |
|------------------------|-----------------------------------------------------------------|
| fastapi                | Main web framework for API endpoints                            |
| uvicorn                | ASGI server for running FastAPI                                 |
| python-dotenv          | Loads environment variables from `.env` files                   |
| python-multipart       | Handles file uploads in FastAPI                                 |
| google-generativeai    | Interface to Google's Gemini AI for data extraction             |
| sqlalchemy             | ORM for managing PostgreSQL database models & sessions          |
| psycopg2-binary        | PostgreSQL database driver                                      |
| pillow                 | Image processing (PIL fork)                                     |
| numpy                  | Numerical processing (required by some image libraries)         |

---

## server.py

This is the main backend application, built with FastAPI. It handles web requests, file uploads, communicates with Gemini AI, and stores data in PostgreSQL.

### Key Features

- **Static Files Serving**: Serves `index.html`, `style.css`, and `app.js` (for Netlify preview/local dev).
- **CORS**: Enabled for all origins, allowing frontend-backend communication.
- **File Upload**: Accepts two Aadhaar card images (front and back).
- **Gemini AI Integration**: Extracts structured info from images.
- **Database ORM**: SQLAlchemy with PostgreSQL (Neon/Render).
- **API Endpoints**: For file upload, static file serving, and health checks.

### Main Components

#### Environment Loading

Loads API keys and database URLs from `.env`:

```python
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
```

#### Database Model

Defines a table for Aadhaar-extracted details:

```python
class DetailsDB(Base):
    __tablename__ = "identity_documents"
    id = Column(Integer, primary_key=True, index=True)
    document_number = Column(String(100), index=True)
    full_name = Column(String(100), index=True)
    date_of_birth = Column(Date, index=True)
    gender = Column(String(100), index=True)
    address = Column(String(255), index=True)
```

#### Gemini AI Integration

Extracts Aadhaar details using Gemini:

```python
model = genai.GenerativeModel('gemini-flash-latest')
prompt = """ Extract the following ... return ONLY the raw JSON object ... """
response = model.generate_content([prompt] + images)
```

#### API Endpoints

##### Health Check

```python
@app.get("/hello")
async def hello():
    return {"message": "Server is running the latest code!"}
```

##### Serve Static Files

- `/` → `index.html`
- `/app.js` → `app.js`
- `/style.css` → `style.css`

##### File Upload

```python
@app.post("/file/upload")
async def upload_file(files: List[UploadFile] = File(...)):
    # ... process images, extract data, store in DB ...
```

---

### Backend API Endpoints

#### GET `/hello`

##### Health Check Endpoint

Checks if the backend is running.

```api
{
    "title": "Health Check",
    "description": "Returns a message if the server is running.",
    "method": "GET",
    "baseUrl": "https://idinsight-backend.onrender.com",
    "endpoint": "/hello",
    "headers": [],
    "queryParams": [],
    "pathParams": [],
    "bodyType": "none",
    "requestBody": "",
    "responses": {
        "200": {
            "description": "Server is live.",
            "body": "{\n  \"message\": \"Server is running the latest code!\"\n}"
        }
    }
}
```

---

#### GET `/`

##### Serve index.html

Serves the main HTML file for the web app.

```api
{
    "title": "Get Main Page",
    "description": "Returns the index.html file for the frontend application.",
    "method": "GET",
    "baseUrl": "https://idinsight-backend.onrender.com",
    "endpoint": "/",
    "headers": [],
    "queryParams": [],
    "pathParams": [],
    "bodyType": "none",
    "requestBody": "",
    "responses": {
        "200": {
            "description": "HTML content.",
            "body": "<!DOCTYPE html> ..."
        },
        "404": {
            "description": "Not Found",
            "body": "Error: index.html not found ..."
        }
    }
}
```

---

#### GET `/app.js`

##### Serve JavaScript File

```api
{
    "title": "Get JavaScript",
    "description": "Returns the app.js JavaScript file for the frontend.",
    "method": "GET",
    "baseUrl": "https://idinsight-backend.onrender.com",
    "endpoint": "/app.js",
    "headers": [],
    "queryParams": [],
    "pathParams": [],
    "bodyType": "none",
    "requestBody": "",
    "responses": {
        "200": {
            "description": "Returns the JavaScript file.",
            "body": "// app.js contents"
        },
        "404": {
            "description": "Not Found",
            "body": "{ \"error\": \"app.js not found ...\" }"
        }
    }
}
```

---

#### GET `/style.css`

##### Serve CSS File

```api
{
    "title": "Get Stylesheet",
    "description": "Returns the style.css file for the frontend.",
    "method": "GET",
    "baseUrl": "https://idinsight-backend.onrender.com",
    "endpoint": "/style.css",
    "headers": [],
    "queryParams": [],
    "pathParams": [],
    "bodyType": "none",
    "requestBody": "",
    "responses": {
        "200": {
            "description": "Returns the CSS file.",
            "body": "/* style.css contents */"
        },
        "404": {
            "description": "Not Found",
            "body": "{ \"error\": \"style.css not found ...\" }"
        }
    }
}
```

---

#### POST `/file/upload`

##### Aadhaar Card Image Upload & Extraction

This is the main API endpoint for uploading Aadhaar card images and extracting identity info.

```api
{
    "title": "Aadhaar File Upload",
    "description": "Upload two Aadhaar images (front/back). Extracts and stores identity info.",
    "method": "POST",
    "baseUrl": "https://idinsight-backend.onrender.com",
    "endpoint": "/file/upload",
    "headers": [
        {
            "key": "Content-Type",
            "value": "multipart/form-data",
            "required": true
        }
    ],
    "queryParams": [],
    "pathParams": [],
    "bodyType": "form",
    "formData": [
        {
            "key": "files",
            "value": "Image files (front and back of Aadhaar card)",
            "required": true
        }
    ],
    "requestBody": "",
    "responses": {
        "200": {
            "description": "Success, data extracted and stored.",
            "body": "{\n  \"status\": \"success\",\n  \"message\": \"Data saved to Neon database!\",\n  \"record_id\": 123,\n  \"extracted_data\": {\n    \"full_name\": \"...\",\n    \"gender\": \"...\",\n    \"date_of_birth\": \"YYYY-MM-DD\",\n    \"document_number\": \"...\",\n    \"address\": \"...\"\n  },\n  \"filenames\": [\"front.jpg\", \"back.jpg\"]\n}"
        },
        "400": {
            "description": "Too few files.",
            "body": "{ \"status\": \"error\", \"message\": \"Please upload at least 2 images (front and back).\" }"
        },
        "500": {
            "description": "Processing or database error.",
            "body": "{ \"status\": \"error\", \"message\": \"Gemini/Processing error: ...\" }"
        }
    }
}
```

---

### Architecture Flow

Below is a high-level flowchart describing the main data flow and system architecture:

```mermaid
flowchart TD
    A[User uploads Aadhaar images] --> B[Frontend (Netlify)]
    B -->|POST /file/upload| C[Backend FastAPI (Render)]
    C --> D[Gemini AI Extraction]
    D --> E[Extracted Data]
    E --> F[Database (PostgreSQL Neon)]
    F --> G[Store Data]
    C -->|Response| B
    B --> A
```

---

## index.html

This is the main HTML file for the CheckInID web application.

### Purpose

- **UI Entry Point**: Renders the main interface for users to upload Aadhaar images.
- **File Inputs**: Provides drag-and-drop & browse for front/back images.
- **Submission**: Button to trigger upload and processing.

### Structure

- **Header**: App title, logo SVG, and subtitle.
- **Main Section**: Two file upload cards (front/back), each with drag-and-drop, file info, and hints.
- **Submit Button**: Triggers the upload process.
- **Script Inclusion**: Loads `app.js` for interactive logic.

---

## style.css

Defines the design system and styling for the whole web application.

### Purpose

- **Theme**: Uses a modern dark theme with accent colors.
- **Layout**: Makes the UI clean and centered.
- **File Upload Styling**: Custom drag-and-drop boxes, buttons, and file info.
- **Responsiveness**: Ensures good appearance on different devices.

### Highlights

- Uses CSS variables for easy theme adjustments.
- Styled upload cards with hover states.
- Distinct color for selected file info and buttons.

---

## app.js

This is the main client-side JavaScript powering interactivity on the web application.

### Purpose

- **File Selection UI**: Shows file names and sizes when selected.
- **Error Handling**: Global error alert for debugging.
- **Submission Logic**: Handles upload button, collects files, sends them to backend, shows status.
- **API Communication**: Sends files to the `/file/upload` endpoint on the Render backend.
- **User Feedback**: Alerts for success and errors, disables button while processing.

### Key Functions

- **File Input Listeners**: Update UI when files are chosen.
- **Submit Button Logic**: Collects files, creates `FormData`, sends POST to backend, parses response.
- **Error Handling**: Alerts user on all errors, both client and server.

---

## Hosting & Deployment

- **Frontend**: Deployed on Netlify (serves static files and app UI).
- **Backend**: Hosted on Render (exposes API endpoints).
- **CORS Enabled**: Allows frontend to call backend APIs cross-origin.
- **Environment Variables**: Sensitive info (API keys, DB URLs) loaded from `.env`.

---

```card
{
    "title": "Production URLs",
    "content": "Frontend is hosted on Netlify, backend API hosted on Render. Ensure CORS is enabled for cross-origin requests."
}
```

---

## Summary Table

| File Name        | Purpose                                             | Hosted On          |
|------------------|-----------------------------------------------------|--------------------|
| requirements.txt | Backend Python dependencies                         | -                  |
| server.py        | FastAPI backend API, Gemini integration, DB         | Render             |
| index.html       | Main web UI                                         | Netlify            |
| style.css        | Application styling                                 | Netlify            |
| app.js           | Frontend logic, handles upload & API integration    | Netlify            |

---

```card
{
    "title": "Best Practice",
    "content": "Keep .env files secure and NEVER expose secrets in frontend code."
}
```

---

## Final Notes

- Users upload images via the Netlify site.
- Images are sent to the FastAPI backend on Render.
- Backend uses Gemini AI to extract identity data from images.
- Results are stored in PostgreSQL and returned to the user with a check-in ID.
- The project architecture is modular and easily extensible for new document types or additional fields.

---

If you have any further questions about a specific module or need code walk-throughs, let me know!
