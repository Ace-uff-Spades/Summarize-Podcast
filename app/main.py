from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import uuid
import os
from app.summarize_agent import summarize_agent

"""
Run the FastAPI server with: uvicorn app.main:app --reload
"""

app = FastAPI()

# Optional: allow frontend access during dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend domain in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/summarize", response_class=HTMLResponse)
async def summarize(file: UploadFile = File(...)):
    try:
        file_path = os.path.join(UPLOAD_DIR, f"{file.filename}")

        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        html_output = summarize_agent(file_path, "./outputs/Notes_formatted_summary.html")

        return HTMLResponse(content=html_output, status_code=200)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)