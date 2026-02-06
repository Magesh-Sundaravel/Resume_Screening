import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

def match_resume_to_job(resume_details: dict, job_description: str) -> dict:
    """Compare resume details with job description"""
    try:
        with open("./prompts/match_job.txt", "r") as file:
            prompt = file.read()
        
        comparison_text = f"""
        RESUME DETAILS:
        {json.dumps(resume_details, indent=2)}

        JOB DESCRIPTION:
        {job_description}

        Analyze how well this resume matches the job description.
        """
        
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": comparison_text}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.2,
        )
        
        match_text = response.choices[0].message.content.strip()
        
        # Clean markdown formatting
        if match_text.startswith("```json"):
            match_text = match_text[7:]
        if match_text.startswith("```"):
            match_text = match_text[3:]
        if match_text.endswith("```"):
            match_text = match_text[:-3]
        
        match_result = json.loads(match_text.strip())
        return match_result
    
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return {"error": "Failed to parse match result", "raw_response": match_text}
    
    except Exception as e:
        print(f"Error matching resume to job: {e}")
        return {"error": str(e)}