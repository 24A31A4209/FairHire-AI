import google.generativeai as genai
import json
import re
import os

# --- Configuration ---
# Note: In a production environment, use os.environ.get("GOOGLE_API_KEY")
api_key = os.environ.get("GOOGLE_API_KEY") 

if api_key:
    genai.configure(api_key=api_key)
else:
    print("❌ Secret not found! Check the name in Settings.")
    

def rank_resume(resume_text, role, requirements):
    # 1. TRUNCATE INPUT
    if len(resume_text) > 15000: 
        resume_text = resume_text[:15000] + "... [truncated]"

    # 2. UPDATED PROMPT LOGIC
    prompt = f"""
    AUDIT TARGET: {role}
    REQUIREMENTS: {requirements}
    RESUME DATA: {resume_text}

    STRICT OUTPUT RULES:
    1. VERIFIED STRENGTHS: Only list a skill here if it DIRECTLY matches the REQUIREMENTS or the ROLE. 
       - If there are NO matching strengths, the list MUST be empty: [].
       - Do NOT list soft skills unless explicitly required.
    
    2. CRITICAL DEFICITS: List the most important missing technical skills from the requirements.
    
    3. BIAS MITIGATION: Ensure you hide the candidate's personal identity.

    SCORING LOGIC (Total 100 pts):
    - CORE TECH (+40 pts): Match against required tools.
    - DOMAIN MATCH (+30 pts): Align with {role}.
    - ANALYTICS (+20 pts): Viz/Stats.
    - SENIORITY (+10 pts): 2+ years exp.

    OUTPUT ONLY VALID JSON:
    {{
        "score": integer,
        "tech_coverage": integer,
        "reason_selected": "string",
        "limitations": "string",
        "skills_found": [],
        "interview_questions": [],
        "logic": "string"
    }}
    """
    
    try:
        # Use the 2026 high-volume workhorse model
        model = genai.GenerativeModel("gemini-3.1-flash-lite-preview")

        # Call the AI
        response = model.generate_content(prompt)
        
        # Ensure we have a valid response
        if not response:
            raise ValueError("No response object returned from API.")
            
        # Robust text extraction (handles safety blocks)
        try:
            content = response.text 
        except ValueError:
            # If the response was blocked by safety filters
            content = str(response.candidates[0].content.parts[0].text) if response.candidates else ""
        
        if not content:
            raise ValueError("The AI returned an empty response.")
        
        # 4. CLEAN AND ISOLATE JSON
        content = re.sub(r'```json\s*|```', '', content).strip()
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        
        if not json_match:
            raise ValueError("AI response did not contain valid JSON formatting.")

        clean_content = json_match.group(0)
        parsed_json = json.loads(clean_content) 
        
        # 5. SCORE VALIDATION
        if "score" in parsed_json:
            if isinstance(parsed_json["score"], str):
                nums = re.findall(r'\d+', parsed_json["score"])
                parsed_json["score"] = int(nums[0]) if nums else 0
        
        return json.dumps(parsed_json)

    except Exception as e:
        print(f"❌ Neural Audit Error: {str(e)}")
        error_response = {
            "score": 0,
            "tech_coverage": 0,
            "reason_selected": "Audit system failure.", 
            "limitations": f"Technical Detail: {str(e)}", 
            "skills_found": [],
            "interview_questions": [],
            "logic": "Check API key quota or model identifier."
        }
        return json.dumps(error_response)
