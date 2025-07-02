from fileinput import filename
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import uuid
import os
import logging
import time
from pathlib import Path
from app.summarize_agent import summarize_agent

"""
Run the FastAPI server with: uvicorn app.main:app --reload
"""

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Optional: allow frontend access during dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend domain in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
UPLOAD_DIR = "uploads"
ALLOWED_MIME_TYPES = ["application/pdf"]
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.post("/summarize", response_class=HTMLResponse)
async def summarize(file: UploadFile = File(...)):
    try:
        logger.info(f"Processing file: {file.filename}")
        
        # Validate file type
        if not file.content_type in ALLOWED_MIME_TYPES:
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        if file.size is not None and file.filename is not None:
            # Validate file size
            if file.size > MAX_FILE_SIZE:
                raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB")
            
            # Create unique filename to prevent conflicts
            file_extension = Path(file.filename).suffix
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = os.path.join(UPLOAD_DIR, unique_filename)

        # Save uploaded file
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        try:
            # Process the file
            html_output = summarize_agent(file_path, "./outputs/Notes_formatted_summary.html")
            logger.info("Summary generated successfully")
            return HTMLResponse(content=html_output, status_code=200)
        finally:
            # Clean up uploaded file
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up temporary file: {file_path}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        return JSONResponse(content={"error": "Internal server error"}, status_code=500)