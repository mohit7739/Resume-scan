import os
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils.extraction import extract_skills

MODEL_PATH = "models/categorizer.pkl"

def load_model():
    """Loads the categorization model from disk."""
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, 'rb') as f:
            return pickle.load(f)
    return None

def predict_category(text):
    """Predicts the category of a resume based on its text."""
    model = load_model()
    if model:
        prediction = model.predict([text])
        return prediction[0]
    return "Uncategorized (Model Not Found)"

def calculate_similarity(resume_text, jd_text):
    """
    Calculates the cosine similarity between a resume and a job description.
    Returns a score from 0 to 100.
    """
    if not jd_text or not resume_text:
        return 0.0
        
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform([jd_text, resume_text])
    
    # Calculate cosine similarity between the two vectors
    similarity_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    
    return round(similarity_score * 100, 2)

def calculate_skill_gap(resume_text, jd_text):
    """
    Identifies skills present in the JD but missing in the resume.
    """
    if not jd_text:
        return []
        
    jd_skills = extract_skills(jd_text)
    resume_skills = extract_skills(resume_text)
    
    # Skills in JD not in resume
    missing_skills = [skill for skill in jd_skills if skill not in resume_skills]
    
    return missing_skills

def rank_candidates(candidates_df, jd_text):
    """
    Ranks a dataframe of candidates based on JD similarity.
    """
    if candidates_df.empty or not jd_text:
        return candidates_df
        
    # Calculate score for each candidate
    candidates_df['Match Score (%)'] = candidates_df['raw_text'].apply(
        lambda x: calculate_similarity(x, jd_text)
    )
    
    # Sort descending
    ranked_df = candidates_df.sort_values(by='Match Score (%)', ascending=False)
    
    return ranked_df
