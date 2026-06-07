import os
import pickle
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Dummy data generator for demonstration
# In a real scenario, you'd load a CSV like 'Resume.csv' with 'Resume_str' and 'Category'
DUMMY_DATA = [
    ("Software Developer", "Python Java C++ backend developer SQL database REST API Django Flask Git Agile problem solving scalability microservices AWS Docker Kubernetes"),
    ("Software Developer", "Frontend developer React Angular Vue.js JavaScript HTML CSS Node.js UI UX responsive design frontend performance Webpack Redux"),
    ("Data Scientist", "Python R machine learning deep learning Pandas NumPy Scikit-Learn TensorFlow PyTorch NLP computer vision statistical analysis SQL Spark big data modeling"),
    ("Data Scientist", "Data analysis Python Pandas visualization Matplotlib Seaborn Tableau PowerBI statistics probability AB testing regression classification cluster analysis"),
    ("Machine Learning Engineer", "Python PyTorch TensorFlow deep learning neural networks computer vision natural language processing Transformers HuggingFace MLOps model deployment CI/CD Git AWS SageMaker"),
    ("Web Developer", "HTML CSS JavaScript PHP MySQL Apache Nginx WordPress web development frontend backend responsive CSS3 HTML5 Git GitHub REST APIs jQuery"),
    ("UI/UX Designer", "Figma Adobe XD Sketch wireframing prototyping user research usability testing visual design user interface user experience UI UX mobile design web design interaction design"),
    ("Digital Marketer", "SEO SEM Google Analytics content marketing social media marketing Facebook Ads Google Ads email marketing campaign management ROI tracking copywriting SEO optimization"),
]

def train_and_save_model(model_path="models/categorizer.pkl"):
    """Trains a simple resume categorization model and saves it."""
    print("Generating training data...")
    # Expand dummy data by adding noise/duplication to make it trainable
    expanded_data = []
    for _ in range(20): # Duplicate and slight variations
        for cat, text in DUMMY_DATA:
            expanded_data.append({"Category": cat, "Text": text})
            
    df = pd.DataFrame(expanded_data)
    
    # Text vectorization and model pipeline
    print("Training model...")
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(stop_words='english', max_features=500)),
        ('clf', LinearSVC(random_state=42, dual=False))
    ])
    
    X = df['Text']
    y = df['Category']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    pipeline.fit(X_train, y_train)
    
    # Evaluate
    y_pred = pipeline.predict(X_test)
    print("\nModel Evaluation:")
    print(classification_report(y_test, y_pred))
    
    # Save the model
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    with open(model_path, 'wb') as f:
        pickle.dump(pipeline, f)
    
    print(f"Model successfully saved to {model_path}")

if __name__ == "__main__":
    train_and_save_model()
