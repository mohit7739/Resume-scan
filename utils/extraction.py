import os
import re
import spacy
import pdfplumber
import docx

# Load spaCy NLP model (make sure to run: python -m spacy download en_core_web_sm)
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading en_core_web_sm...")
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

# Define a simple dictionary of skills for extraction (this can be expanded)
SKILLS_DB = [
    "python", "java", "c++", "c#", "javascript", "typescript", "html", "css", "react", "angular", "vue", 
    "node.js", "django", "flask", "fastapi", "spring boot", "sql", "mysql", "postgresql", "mongodb", 
    "aws", "azure", "gcp", "docker", "kubernetes", "git", "linux", "machine learning", "deep learning", 
    "nlp", "computer vision", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "tableau", "powerbi",
    "excel", "agile", "scrum", "jira", "figma", "adobe xd", "ui/ux", "seo", "digital marketing", "data analysis",
    "statistics", "regression", "communication", "leadership"
]

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
    return text

def extract_text_from_docx(docx_path):
    """Extracts text from a DOCX file."""
    text = ""
    try:
        doc = docx.Document(docx_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"Error reading DOCX {docx_path}: {e}")
    return text

def extract_email(text):
    """Extracts email addresses from text."""
    email = re.findall(r"[\w\.-]+@[\w\.-]+", text)
    return email[0] if email else None

def extract_phone(text):
    """Extracts phone numbers from text."""
    phone = re.findall(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
    return phone[0] if phone else None

def extract_links(text):
    """Extracts LinkedIn and GitHub URLs from text."""
    linkedin = None
    github = None
    
    urls = re.findall(r"(https?://[^\s]+)", text)
    for url in urls:
        if "linkedin.com" in url.lower():
            linkedin = url
        elif "github.com" in url.lower():
            github = url
            
    return linkedin, github

def extract_skills(text):
    """Extracts skills from text based on a predefined dictionary."""
    skills = []
    text_lower = text.lower()
    for skill in SKILLS_DB:
        # Use regex for exact word match
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text_lower):
            skills.append(skill.title())
    return list(set(skills))

def extract_name(text):
    """Attempts to extract a name using spaCy NER. Usually found at the beginning."""
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            # Just taking the first person entity as a naive approach
            return ent.text.strip()
    return None

def parse_resume(file_path):
    """Parses a resume file and extracts structured information."""
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == ".pdf":
        text = extract_text_from_pdf(file_path)
    elif ext in [".docx", ".doc"]:
        text = extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")
        
    linkedin, github = extract_links(text)
    
    data = {
        "name": extract_name(text) or "Unknown",
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
        "education": "Not extracted in MVP", # Advanced NER needed for reliable extraction
        "experience": "Not extracted in MVP", # Advanced NER needed
        "certifications": [],
        "projects": [],
        "location": None,
        "linkedin": linkedin,
        "github": github,
        "raw_text": text,
        "filename": os.path.basename(file_path)
    }
    
    return data
