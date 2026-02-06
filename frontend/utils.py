import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Use environment variable with fallback for local development
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def upload_and_extract_resume(file):
    """Upload resume file to backend and extract details"""
    try:
        # Reset file pointer to beginning
        file.seek(0)
        files = {"file": (file.name, file, file.type)}
        response = requests.post(
            f"{BACKEND_URL}/extract-resume", 
            files=files,
            timeout=120  # 2 minutes timeout
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. Please try again."}
    except requests.exceptions.ConnectionError:
        return {"error": f"Cannot connect to backend at {BACKEND_URL}. Please check if the backend is running."}
    except requests.exceptions.RequestException as e:
        return {"error": f"Request error: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

def match_with_job(resume_details, job_description):
    """Send resume details and job description to backend for matching"""
    try:
        payload = {
            "resume_details": resume_details,
            "job_description": job_description
        }
        response = requests.post(
            f"{BACKEND_URL}/match-job", 
            json=payload,
            timeout=120
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. Please try again."}
    except requests.exceptions.ConnectionError:
        return {"error": f"Cannot connect to backend at {BACKEND_URL}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Request error: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

def complete_analysis(file, job_description):
    """Complete analysis in one API call"""
    try:
        # Reset file pointer to beginning
        file.seek(0)
        files = {"file": (file.name, file, file.type)}
        data = {"job_description": job_description}
        response = requests.post(
            f"{BACKEND_URL}/analyze", 
            files=files, 
            data=data,
            timeout=240  # 4 minutes for complete analysis
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. The analysis is taking too long. Please try again."}
    except requests.exceptions.ConnectionError:
        return {"error": f"Cannot connect to backend at {BACKEND_URL}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Request error: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}