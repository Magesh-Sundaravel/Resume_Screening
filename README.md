# AI Resume Screening

AI-powered resume matching system with FastAPI backend and Streamlit frontend.

## Setup with UV

### 1. Install UV
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clone and Setup Project
```bash
# Clone repository
git clone <your-repo-url>
cd resume-screening

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -e .
```

### 3. Configure Environment
```bash
# Create .env file
cp .env.example .env

# Edit .env and add your GROQ_API_KEY
```

### 4. Create Required Directories
```bash
mkdir -p prompts uploads
```

### 5. Add Prompt Files
Create `prompts/extract_resume.txt` and `prompts/match_job.txt` with the content provided above.

### 6. Run the Application

**Terminal 1 - Start Backend:**
```bash
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Start Frontend:**
```bash
uv run streamlit run frontend/app.py
```

### 7. Access the Application
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Development

### Add New Dependencies
```bash
uv pip install <package-name>
uv pip freeze > requirements.txt
```

### Format Code
```bash
uv run black .
uv run ruff check .
```

### Run Tests
```bash
uv run pytest
```

## Project Structure
```
resume-screening/
├── backend/          # FastAPI backend
├── frontend/         # Streamlit UI
├── prompts/          # LLM prompts
├── uploads/          # Temporary file storage
├── pyproject.toml    # Project configuration
└── .env             # Environment variables
```
