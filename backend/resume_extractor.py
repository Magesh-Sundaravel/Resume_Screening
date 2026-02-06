import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
    timeout=60.0, 

)

def extract_resume_details(resume_text: str) -> dict:
    """Extract structured information from resume text"""
    try:
        with open("./prompts/extract_resume.txt", "r") as file:
            prompt = file.read()
        
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": prompt},
                {
                    "role": "user",
                    "content": f"Extract information from this resume:\n\n{resume_text}"
                }
            ],
            model="llama-3.1-8b-instant",
            temperature=0.1,
            max_tokens=2000,  

        )
        
        extracted_text = response.choices[0].message.content.strip()
        
        # Clean markdown formatting
        if extracted_text.startswith("```json"):
            extracted_text = extracted_text[7:]
        if extracted_text.startswith("```"):
            extracted_text = extracted_text[3:]
        if extracted_text.endswith("```"):
            extracted_text = extracted_text[:-3]
        
        extracted_details = json.loads(extracted_text.strip())
        return extracted_details
    
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return {"error": "Failed to parse resume", "raw_response": extracted_text}
    
    except Exception as e:
        print(f"Error extracting resume: {e}")
        return {"error": str(e)}