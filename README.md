# AI-Powered Resume Screening System

This is a full-stack AI-powered Resume Screening System built with Python, Streamlit, Pandas, scikit-learn, and NLP techniques.

## Features

- **Resume Upload:** Upload PDF and DOCX files individually or in batches.
- **NLP Information Extraction:** Automatically extracts Name, Email, Phone, Skills, Education, Experience, and Links using spaCy and Regular Expressions.
- **Resume Categorization:** Categorizes resumes (e.g., Software Developer, Data Scientist) using a Machine Learning model.
- **Resume Ranking:** Compares uploaded resumes against a provided Job Description (JD) using TF-IDF and Cosine Similarity, generating a match score.
- **Dashboard & Analytics:** View total uploads, top candidates, category distributions, and skill gap analysis via an interactive Streamlit dashboard.
- **Export Functionality:** Export shortlisted candidates to CSV or Excel.

## Setup Instructions

1. **Clone the repository or navigate to the directory.**
2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Download NLP models:**
   ```bash
   python -m spacy download en_core_web_sm
   ```
5. **Run the initial setup scripts:**
   - (Optional) Run the model trainer script if you want to generate a fresh categorization model: `python utils/model_trainer.py`
6. **Run the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

## Folder Structure
- `data/`: SQLite database storage.
- `models/`: Pre-trained ML models.
- `uploads/`: Temporary storage for uploaded resumes.
- `utils/`: Core processing scripts (extraction, scoring, db, ui_components).
- `app.py`: Main Streamlit application.
# Resume-scan
