# 🎯 HireMatch AI – AI-Based Resume Screening and Job Matching System

HireMatch AI is an intelligent recruitment screening and applicant ranking platform powered by Natural Language Processing (NLP) and machine-learning techniques. It automates candidate profile extraction, evaluates alignment against job requirements, identifies skill gaps, and ranks applicants with explainable analytics.

---

## 3. Problem Statement
Recruitment processes often involve manually reviewing a large number of resumes, which is time-consuming and may lead to inconsistent evaluation or overlooking suitable candidates. Recruiters need an efficient way to identify applicants whose skills, qualifications, education, and experience align with job requirements. HireMatch AI supports this process through automated resume analysis and job matching.

## 4. Objectives & Core Capabilities

| Objective | Implemented Capability |
| :--- | :--- |
| **1. Automate Resume Screening** | Multi-format ingestion supporting **PDF** (`pdfplumber` + `pypdf`), **DOCX** (`python-docx`), and **TXT** files with automated text standardization. |
| **2. Information Extraction** | Extracts **Candidate Name, Email, Phone, Social Profiles (LinkedIn, GitHub)**, **Categorized Technical & Soft Skills**, **Education Degrees & Universities**, and **Work Experience duration**. |
| **3. Job Matching & Scoring** | Computes multi-factor composite match scores combining **Semantic Cosine Similarity (TF-IDF)**, **Required vs Preferred Skills Overlap**, **Experience Delta**, and **Degree Hierarchy Alignment**. |
| **4. Candidate Ranking** | Ranks applicants descending by overall match score, assigns fit tier badges (🌟 *Top Match*, ⚡ *Potential Fit*, ⚠️ *Low Alignment*), and provides interactive recruiter filtering. |
| **5. Explainable AI & Gap Analysis** | Highlights candidate strengths, missing mandatory competencies, actionable upskilling recommendations, and generates **tailored interview questions**. |

---

## 🏗️ Architecture & Pipeline

```text
                                [ Resumes (PDF, DOCX, TXT) ]
                                              │
                                              ▼
                             ┌─────────────────────────────────┐
                             │    Document Parser & Cleaner    │
                             └────────────────┬────────────────┘
                                              ▼
                             ┌─────────────────────────────────┐
                             │       NLP Entity Extractor      │
                             │  - Skills Taxonomy Matcher      │
                             │  - Degree & University Parser   │
                             │  - Date & Experience Calculator │
                             │  - Contact & Profile Links      │
                             └────────────────┬────────────────┘
                                              │
                      ┌───────────────────────┴───────────────────────┐
                      ▼                                               ▼
         ┌────────────────────────┐                     ┌────────────────────────┐
         │  Job Profile Matching  │                     │ Semantic Vectorization │
         │  - Required Skills     │                     │ - TF-IDF n-grams (1,2) │
         │  - Experience Gap      │                     │ - Cosine Similarity    │
         │  - Education Tier      │                     └───────────┬────────────┘
         └────────────┬───────────┘                                 │
                      └───────────────────────┬─────────────────────┘
                                              ▼
                             ┌─────────────────────────────────┐
                             │   Weighted Composite Matcher    │
                             │  (Recruiter Real-time Weights)  │
                             └────────────────┬────────────────┘
                                              ▼
                             ┌─────────────────────────────────┐
                             │    Applicant Ranking & Tiers    │
                             │  - Leaderboard Bar Charts       │
                             │  - Multi-Axis Radar Profiler    │
                             │  - Skill Gap & Interview Prompts│
                             │  - CSV / JSON / HTML Export     │
                             └─────────────────────────────────┘
```

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.9+ (Python 3.13 tested and verified)
- Modern Web Browser (Chrome, Edge, Firefox, Safari)

### 1. Installation
The virtual environment is already pre-configured in `venv/`. If setting up in a new environment:
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows CMD)
venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt

# Download NLTK data
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('punkt_tab')"
```

### 2. Launch the Web Application
Run using the virtual environment python:
```bash
.\venv\Scripts\streamlit.exe run app.py
```
*Or double click on `run.bat`.*

Open your browser to: **`http://localhost:8501`**

---

## 💻 Features Walkthrough

### 1. Candidate Leaderboard & Rankings
- **Cohort KPI Cards:** Instant metrics showing Total Applicants, Top Match count, Average Cohort Score, and Average Experience.
- **Interactive Leaderboard:** Plotly horizontal bar chart color-coded by fit tier.
- **Recruiter Filters:** Filter candidates by minimum overall match percentage and mandatory required skills.
- **Data Export:** Export the complete ranking table to **CSV** or structured **JSON**.

### 2. Candidate Deep-Dive & Explainable AI
- **Multi-Axis Radar Chart:** Visual comparison of candidate performance against a 100% target benchmark across **Skills**, **Semantic Alignment**, **Experience**, and **Education**.
- **Skills Distribution Donut:** Visual breakdown of Matched Required, Matched Preferred, and Missing Skills.
- **Skills Alignment Matrix:** Color-coded badges for exact matches (green), missing skills (red), and bonus candidate skills (gray).
- **Explainable Skill Gap Report:** Concrete breakdown of candidate strengths, experience delta, and hiring verdict.
- **Tailored Interview Questions:** Dynamically generated technical and behavioral interview questions tailored to each candidate's background and skill gaps.
- **Downloadable Candidate Card:** Generate a printable HTML candidate summary card.

### 3. Batch Resume Ingestion
- Upload multiple resumes simultaneously in **PDF**, **DOCX**, or **TXT** format.
- **Instant Demo Button:** Load 5 pre-built diverse resumes (`sample_data/resumes/`) with a single click.

### 4. Job Description Studio
- Pre-loaded role templates:
  - *Senior Data Scientist*
  - *Full-Stack Software Engineer*
  - *AI / Machine Learning Engineer*
- Or create a custom job posting with custom required skills, experience thresholds, and education criteria.
- Real-time skills extraction analyzer that detects technical keywords from job descriptions.

### 5. Optional Gemini AI Synthesis
- Provide an optional Google Gemini API key in the sidebar for executive AI summaries and deep candidate evaluations.
- 100% operational offline without any API keys using local NLP heuristics.

---

## 🧪 Running the Unit Tests

Execute the automated test suite verifying parser, entity extraction, matching, ranking, and report generation:

```bash
.\venv\Scripts\python.exe -m unittest tests/test_hirematch.py
```

Result:
```text
Ran 8 tests in 0.301s
OK
```

---

## 📁 Project Structure

```text
Hire-match/
├── app.py                      # Main Streamlit application
├── config.py                   # Scoring weights, education tiers, thresholds
├── requirements.txt            # Python dependencies
├── run.bat                     # Windows launch script
├── run.ps1                     # PowerShell launch script
├── README.md                   # System documentation
├── modules/
│   ├── parser.py               # PDF, DOCX, TXT document parser
│   ├── extractor.py            # Information & entity extraction
│   ├── skills_database.py      # Curated taxonomy and synonym mapping
│   ├── matcher.py              # Semantic TF-IDF and weighted composite matching
│   ├── ranker.py               # Candidate ranking, filtering, cohort analytics
│   ├── explainer.py            # Skill gap analysis & interview questions
│   ├── visualizer.py           # Plotly radar, leaderboard, and donut charts
│   ├── ai_enricher.py          # Optional Gemini API synthesis
│   └── report_generator.py     # CSV, JSON, and HTML exports
├── sample_data/
│   ├── jobs/                   # Pre-configured job profiles (JSON)
│   └── resumes/                # 5 diverse sample resumes for testing
└── tests/
    └── test_hirematch.py       # Automated unit test suite
```
