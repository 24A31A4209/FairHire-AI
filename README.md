---
title: FairHire AI
emoji: ⚖️
colorFrom: blue
colorTo: indigo
sdk: Dockerfile
pinned: false
---

# ⚖ FairHire AI — AI-Powered Fair Hiring System with Bias Detection

> **Hack2Skills Solution Challenge 2026**
> Domain: *Unbiased AI Decision — Ensuring Fairness & Detecting Bias*

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![SBERT](https://img.shields.io/badge/SBERT-all--MiniLM--L6--v2-orange)
![License](https://img.shields.io/badge/License-MIT-purple)

---

## 🎯 Project Overview

FairHire AI is a production-grade, web-based hiring system that:

- **Accepts** multiple resumes (PDF/DOCX) and a job description
- **Ranks** candidates using **Sentence-BERT** semantic matching
- **Detects** 4 types of hiring bias: name, gender, college, and location
- **Removes** biased factors and re-ranks candidates fairly (**Blind Hiring**)
- **Explains** every decision with transparent XAI output

---

## 🏗 Architecture

```
project/
├── frontend/
│   ├── index.html          ← Single-page app (Home + Upload + Results)
│   ├── css/style.css       ← Dark editorial theme
│   └── js/app.js           ← UI logic, API calls, chart rendering
│
├── backend/
│   ├── app.py              ← Flask REST API
│   ├── resume_parser.py    ← PDF/DOCX text extraction + NLP parsing
│   ├── bias_detector.py    ← 4-layer bias detection + redaction
│   ├── matcher.py          ← SBERT / TF-IDF similarity scoring
│   └── explainability.py   ← XAI explanation generator
│
├── dataset/
│   └── sample_resumes.md   ← 5 sample candidate profiles for testing
│
├── uploads/                ← Temporary resume storage (auto-cleaned)
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/your-username/fairhire-ai.git
cd fairhire-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. (Optional) Download spaCy model

```bash
python -m spacy download en_core_web_sm
```

### 3. Run the Flask Server

```bash
cd backend
python app.py
```

### 4. Open in Browser

```
http://localhost:5000
```

> **Note:** The frontend also works standalone (without backend) in **demo mode** — it generates mock analysis data for UI demonstration.

---

## 🧠 AI Pipeline

### Step 1: Text Extraction
- **PDF**: `pdfplumber` → page-by-page text extraction
- **DOCX**: `python-docx` → paragraphs + table cells

### Step 2: Resume Parsing
- Extracts: Skills, Education, Experience (years), Projects, Certifications
- Uses regex patterns + a curated skill keyword bank (50+ technologies)

### Step 3: Bias Detection
```
Bias Type     | What's Detected
──────────────┼──────────────────────────────────────────
Name          | Candidate name in first lines or labeled
Gender        | he/she/him/her/male/female/Mr/Mrs etc.
College       | IIT, MIT, Stanford, NIT, IIM, etc.
Location      | Indian/global city names, state names
```

### Step 4: Blind Hiring (Bias Removal)
- All detected biased fields are **redacted** with placeholder tokens
- Clean resume text is used for fair scoring

### Step 5: SBERT Matching
```python
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")
jd_embedding     = model.encode(job_description)
resume_embedding = model.encode(clean_resume_text)
score = util.cos_sim(jd_embedding, resume_embedding)
```
- **Original Score**: Similarity with raw resume
- **Fair Score**: Similarity with bias-redacted resume

### Step 6: XAI Explanation
- Skills matched / not matched against JD
- Experience years vs. requirement
- Bias impact: how much score changed after removal
- Natural language verdict

---

## 📊 API Reference

### `POST /api/analyze`

**Request** (multipart/form-data):
| Field | Type | Description |
|-------|------|-------------|
| `resumes` | File[] | PDF or DOCX resume files |
| `job_description` | string | Job requirements text |

**Response** (JSON):
```json
{
  "success": true,
  "candidates": [
    {
      "rank": 1,
      "name": "Candidate A",
      "filename": "resume.pdf",
      "original_score": 74.3,
      "fair_score": 91.2,
      "bias_report": {
        "bias_flags": [
          { "type": "name", "value": "...", "risk": "..." },
          { "type": "college", "value": "IIT", "risk": "..." }
        ],
        "bias_score": 30
      },
      "explanation": {
        "skills_matched": ["python", "nlp", "sql"],
        "skills_missing": ["docker"],
        "verdict": "🟢 Strong Match",
        "summary": "Selected because candidate has Python, NLP, SQL ...",
        "ignored_factors": ["name", "college"]
      }
    }
  ],
  "analytics": {
    "total_candidates": 5,
    "total_bias_instances": 12,
    "avg_fair_score": 68.4,
    "bias_breakdown": { "name": 4, "gender": 2, "college": 5, "location": 1 },
    "top_skills": [{ "skill": "python", "count": 5 }]
  }
}
```

---

## 🎨 UI Features

| Feature | Description |
|---------|-------------|
| Drag & Drop Upload | Multi-file PDF/DOCX upload with live file list |
| Quick-fill JDs | One-click sample job descriptions |
| Bias Toggles | Enable/disable each bias type individually |
| Score Comparison Chart | Bar chart: Original vs Fair score per candidate |
| Bias Breakdown Donut | Pie chart of bias types removed |
| Top Skills Bar Chart | Most common skills across candidate pool |
| Candidate Cards | Score bars, skill tags, bias chips, rank medals |
| XAI Modal | Full explanation popup per candidate |
| Demo Mode | Works without backend using generated mock data |

---

## 🔧 Configuration

Edit `backend/bias_detector.py` to:
- Add more elite college names to `ELITE_COLLEGES`
- Add more cities to `LOCATION_PATTERNS`
- Add gender terms to `GENDER_PATTERNS`

Edit `backend/resume_parser.py` to:
- Add more skills to `SKILL_KEYWORDS`

---

## 🌐 Deployment

### Option A: Local (Development)
```bash
python backend/app.py
```

### Option B: Render / Railway
1. Push code to GitHub
2. Create new Web Service on Render
3. Build command: `pip install -r requirements.txt`
4. Start command: `python backend/app.py`

### Option C: Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "backend/app.py"]
```

```bash
docker build -t fairhire-ai .
docker run -p 5000:5000 fairhire-ai
```

---

## 📋 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5, CSS3, Vanilla JavaScript, Chart.js |
| Backend | Python 3.10+, Flask 3.0, Flask-CORS |
| AI Matching | Sentence-BERT (all-MiniLM-L6-v2) |
| Fallback | TF-IDF + Cosine Similarity (scikit-learn) |
| PDF Parsing | pdfplumber |
| DOCX Parsing | python-docx |
| NLP | Regex + spaCy (optional) |

---

## 📈 Hackathon Highlights

**Innovation:** Goes beyond keyword matching — uses semantic NLP to understand *meaning*, not just vocabulary overlap.

**Social Impact:** Directly addresses systemic hiring bias that affects millions of job seekers worldwide.

**Explainability:** Every AI decision is transparent and auditable — no black-box outputs.

**Extensibility:** Bias detection module can be extended with more categories (age, disability, race indicators).

---

## 👥 Team

Built for Hack2Skills Solution Challenge 2026
Domain: Unbiased AI Decision — Ensuring Fairness & Detecting Bias

---

## 📄 License

MIT License — See LICENSE file for details.