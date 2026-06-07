import sqlite3
import pandas as pd
import os
import json

DB_PATH = "data/resumes.db"

def get_connection():
    """Create a database connection to the SQLite database."""
    # Ensure data directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    return conn

def init_db():
    """Initialize the database tables if they do not exist."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create the candidates table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            phone TEXT,
            skills TEXT,
            education TEXT,
            experience TEXT,
            certifications TEXT,
            projects TEXT,
            location TEXT,
            linkedin TEXT,
            github TEXT,
            category TEXT,
            raw_text TEXT,
            filename TEXT,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_candidate(data: dict):
    """Save a parsed candidate dictionary to the database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO candidates (
            name, email, phone, skills, education, experience, 
            certifications, projects, location, linkedin, github, 
            category, raw_text, filename
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("name"),
        data.get("email"),
        data.get("phone"),
        json.dumps(data.get("skills", [])),
        data.get("education"),
        data.get("experience"),
        json.dumps(data.get("certifications", [])),
        json.dumps(data.get("projects", [])),
        data.get("location"),
        data.get("linkedin"),
        data.get("github"),
        data.get("category"),
        data.get("raw_text"),
        data.get("filename")
    ))
    conn.commit()
    conn.close()

def get_all_candidates() -> pd.DataFrame:
    """Retrieve all candidates as a Pandas DataFrame."""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM candidates", conn)
    conn.close()
    
    # Process json columns
    if not df.empty:
        for col in ["skills", "certifications", "projects"]:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: json.loads(x) if pd.notnull(x) and x else [])
    
    return df

def clear_db():
    """Delete all records from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM candidates")
    conn.commit()
    conn.close()
