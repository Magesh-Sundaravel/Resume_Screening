from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import shutil
from pathlib import Path
import PyPDF2
import docx

from backend.resume_extractor import extract_resume_details
from backend.job_matcher import match_resume_to_job
from backend.models import MatchRequest, AnalysisResponse

app = FastAPI(title="Resume Matcher API", version="1.0.0")

# CORS - Allow your frontend domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",  # Local development
        "https://resume-matcher-frontend.onrender.com",  # Production frontend
        "*"  # Remove this in production and specify exact origins
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file"""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")

def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX file"""
    try:
        doc = docx.Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading DOCX: {str(e)}")

def extract_text_from_txt(file_path: str) -> str:
    """Extract text from TXT file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading TXT: {str(e)}")

@app.get("/")
async def root():
    return {
        "message": "Resume Matcher API is running",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "extract": "/extract-resume",
            "match": "/match-job",
            "analyze": "/analyze"
        }
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "resume-matcher-api"
    }

@app.post("/extract-resume")
async def extract_resume(file: UploadFile = File(...)):
    """Extract resume details from uploaded file"""
    file_path = None
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        file_extension = file.filename.split('.')[-1].lower()
        if file_extension not in ['pdf', 'docx', 'txt']:
            raise HTTPException(
                status_code=400, 
                detail="Unsupported file format. Please upload PDF, DOCX, or TXT."
            )
        
        # Save file
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Extract text
        if file_extension == 'pdf':
            resume_text = extract_text_from_pdf(str(file_path))
        elif file_extension == 'docx':
            resume_text = extract_text_from_docx(str(file_path))
        else:  # txt
            resume_text = extract_text_from_txt(str(file_path))
        
        # Validate extracted text
        if not resume_text or len(resume_text.strip()) < 10:
            raise HTTPException(
                status_code=400,
                detail="Could not extract meaningful text from the file. Please check the file content."
            )
        
        # Extract details using LLM
        resume_details = extract_resume_details(resume_text)
        
        # Clean up file
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        
        if "error" in resume_details:
            raise HTTPException(status_code=500, detail=resume_details["error"])
        
        return JSONResponse(content={"resume_details": resume_details})
    
    except HTTPException:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        raise
    except Exception as e:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/match-job")
async def match_job(request: MatchRequest):
    """Match resume details with job description"""
    try:
        match_result = match_resume_to_job(
            request.resume_details, 
            request.job_description
        )
        
        if "error" in match_result:
            raise HTTPException(status_code=500, detail=match_result["error"])
        
        return JSONResponse(content={"match_analysis": match_result})
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze")
async def analyze_resume_and_job(
    file: UploadFile = File(...),
    job_description: str = Form(...)
):
    """Complete analysis: Extract resume and match with job description"""
    file_path = None
    try:
        # Validate inputs
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        if not job_description or len(job_description.strip()) < 10:
            raise HTTPException(
                status_code=400,
                detail="Job description is too short. Please provide a detailed job description."
            )
        
        file_extension = file.filename.split('.')[-1].lower()
        if file_extension not in ['pdf', 'docx', 'txt']:
            raise HTTPException(
                status_code=400, 
                detail="Unsupported file format. Please upload PDF, DOCX, or TXT."
            )
        
        # Save and process file
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Extract text
        if file_extension == 'pdf':
            resume_text = extract_text_from_pdf(str(file_path))
        elif file_extension == 'docx':
            resume_text = extract_text_from_docx(str(file_path))
        else:
            resume_text = extract_text_from_txt(str(file_path))
        
        if not resume_text or len(resume_text.strip()) < 10:
            raise HTTPException(
                status_code=400,
                detail="Could not extract meaningful text from the file."
            )
        
        # Extract resume details
        resume_details = extract_resume_details(resume_text)
        
        if "error" in resume_details:
            raise HTTPException(status_code=500, detail=resume_details["error"])
        
        # Match with job
        match_result = match_resume_to_job(resume_details, job_description)
        
        if "error" in match_result:
            raise HTTPException(status_code=500, detail=match_result["error"])
        
        # Clean up
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        
        return {
            "resume_details": resume_details,
            "match_analysis": match_result
        }
    
    except HTTPException:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        raise
    except Exception as e:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))