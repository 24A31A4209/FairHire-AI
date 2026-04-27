from flask import Flask, render_template, request
import os
import json
import pdfplumber
from backend.matcher import rank_resume
from backend.bias_detector import BiasDetector

app = Flask(__name__)
detector = BiasDetector()

# --- Configurations ---
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------- HELPERS ----------

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text(filepath):
    text = ""
    try:
        if filepath.lower().endswith('.pdf'):
            # Using 'with' correctly to ensure the file closes immediately
            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text(layout=True)
                    if page_text:
                        text += page_text + "\n"
                    page.flush_cache() # Manually clear page cache to save RAM
        
        elif filepath.lower().endswith('.txt'):
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
                
    except Exception as e:
        print(f"❌ Extraction error on {filepath}: {e}")
    
    return text.strip()

# ---------- ROUTE ----------

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        role = request.form.get('role', 'General Applicant').strip()
        requirements = request.form.get('requirements', '').strip()
        files = request.files.getlist('resumes')

        if not files or (len(files) == 1 and files[0].filename == ''):
            return "No files uploaded", 400

        final_results = []

        for file in files:
            if file and allowed_file(file.filename):
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(file_path)

                # 1. Extraction
                raw_text = extract_text(file_path)
                
                if len(raw_text) < 10:
                    print(f"❌ Skipping {file.filename}: No readable text found.")
                    if os.path.exists(file_path): os.remove(file_path)
                    continue

                # 2. Bias removal
                bias_report = detector.detect_bias(raw_text, {})
                safe_text = detector.remove_bias(raw_text, bias_report)

                # 3. AI Analysis - Passing the text here!
                try:
                    # We pass 'safe_text' which contains the resume content
                    raw_analysis = rank_resume(safe_text, role, requirements)
                    
                    # Ensure we handle the JSON response from matcher.py safely
                    analysis_data = json.loads(raw_analysis)
                    
                except Exception as e:
                    print(f"⚠️ Neural Audit failed for {file.filename}: {e}")
                    if os.path.exists(file_path): os.remove(file_path)
                    continue

                # 4. Success: Build the result object
                final_results.append({
                    "filename": file.filename,
                    "score": safe_int(analysis_data.get("score")),
                    "tech_coverage": safe_int(analysis_data.get("tech_coverage")),
                    "reason": analysis_data.get("reason_selected", "Match Found"),
                    "limitations": analysis_data.get("limitations", "None identified"),
                    "skills": analysis_data.get("skills_found", []),
                    "interview_questions": analysis_data.get("interview_questions", []),
                    "logic": analysis_data.get("logic", "Audit Complete"),
                    "fairness": "High (Bias Redacted)",
                    "bias_flags": bias_report.get("bias_flags", [])
                })

                if os.path.exists(file_path):
                    os.remove(file_path)

        if not final_results:
            return "No valid resumes could be processed. Check console for details.", 422

        # Sort and Render
        final_results = sorted(final_results, key=lambda x: x['score'], reverse=True)
        avg_score = sum(r['score'] for r in final_results) // len(final_results)

        return render_template('dashboard.html', results=final_results, role=role, aggregate=avg_score)

    return render_template('index.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860)
