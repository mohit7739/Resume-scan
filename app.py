import streamlit as st
import os
import pandas as pd
import time
from io import BytesIO

# Import utilities
from utils.db import init_db, get_all_candidates, save_candidate, clear_db
from utils.extraction import parse_resume
from utils.scoring import predict_category, calculate_similarity, calculate_skill_gap, rank_candidates
from utils.ui_components import render_metric_card, render_category_distribution, render_top_skills, render_candidate_card, render_skill_pills

# Constants
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Page Config
st.set_page_config(
    page_title="AI Resume Screening System",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for aesthetics
st.markdown("""
<style>
    .main { padding: 2rem; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .reportview-container { background: var(--background-color); }
</style>
""", unsafe_allow_html=True)

# Initialize Database
@st.cache_resource
def setup_db():
    init_db()

setup_db()

# --- Sidebar Navigation ---
st.sidebar.title("📄 AI Resume Screener")
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigation", ["Dashboard", "Upload Resumes", "Candidate Ranking", "Settings"])

# Load Data
df = get_all_candidates()

# --- 1. Dashboard Page ---
if page == "Dashboard":
    st.title("📊 System Dashboard")
    st.markdown("Overview of the resume screening system.")
    
    if df.empty:
        st.info("No resumes uploaded yet. Go to 'Upload Resumes' to get started.")
    else:
        # Metrics Row
        col1, col2, col3 = st.columns(3)
        with col1:
            render_metric_card("Total Resumes", len(df))
        with col2:
            unique_categories = df['category'].nunique() if 'category' in df.columns else 0
            render_metric_card("Unique Categories", unique_categories)
        with col3:
            avg_skills = df['skills'].apply(lambda x: len(x) if isinstance(x, list) else 0).mean()
            render_metric_card("Avg Skills / Resume", round(avg_skills, 1))
            
        st.markdown("---")
        
        # Charts Row
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            st.subheader("Category Distribution")
            render_category_distribution(df)
            
        with col_chart2:
            st.subheader("Top Extracted Skills")
            render_top_skills(df)
            
        st.markdown("---")
        st.subheader("Recent Uploads")
        st.dataframe(df[['name', 'email', 'category', 'filename']].head(10), use_container_width=True)

# --- 2. Upload Resumes Page ---
elif page == "Upload Resumes":
    st.title("📤 Upload Resumes")
    st.markdown("Upload PDF or DOCX files for automatic text extraction and categorization.")
    
    uploaded_files = st.file_uploader("Choose resume files", type=["pdf", "docx"], accept_multiple_files=True)
    
    if st.button("Process Resumes", type="primary") and uploaded_files:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        processed_count = 0
        for i, file in enumerate(uploaded_files):
            status_text.text(f"Processing {file.name}...")
            
            # Save file temporarily
            file_path = os.path.join(UPLOAD_DIR, file.name)
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())
                
            try:
                # 1. Extract text and entities
                candidate_data = parse_resume(file_path)
                
                # 2. Categorize using ML model
                category = predict_category(candidate_data["raw_text"])
                candidate_data["category"] = category
                
                # 3. Save to database
                save_candidate(candidate_data)
                processed_count += 1
                
            except Exception as e:
                st.error(f"Error processing {file.name}: {str(e)}")
            finally:
                # Clean up temporary file
                if os.path.exists(file_path):
                    os.remove(file_path)
                    
            # Update progress
            progress = (i + 1) / len(uploaded_files)
            progress_bar.progress(progress)
            
        status_text.text("Processing complete!")
        st.success(f"Successfully processed {processed_count} resumes.")
        st.balloons()
        time.sleep(2)
        st.rerun()

# --- 3. Candidate Ranking Page ---
elif page == "Candidate Ranking":
    st.title("🏆 Candidate Ranking")
    st.markdown("Enter a Job Description to rank the database of candidates based on similarity.")
    
    if df.empty:
        st.warning("Please upload resumes first.")
    else:
        # Layout
        col_jd, col_results = st.columns([1, 2])
        
        with col_jd:
            st.subheader("Job Description")
            jd_text = st.text_area("Paste the job description here...", height=300)
            
            # Filtering Options
            st.markdown("### Filters")
            categories = ["All"] + list(df['category'].dropna().unique())
            selected_category = st.selectbox("Filter by Category", categories)
            
            rank_button = st.button("Rank Candidates", type="primary")
            
        with col_results:
            st.subheader("Results")
            
            if rank_button and jd_text:
                with st.spinner("Calculating match scores and skill gaps..."):
                    # Apply category filter
                    filtered_df = df.copy()
                    if selected_category != "All":
                        filtered_df = filtered_df[filtered_df['category'] == selected_category]
                        
                    # Rank candidates
                    ranked_df = rank_candidates(filtered_df, jd_text)
                    
                    if ranked_df.empty:
                        st.info("No candidates match the selected filters.")
                    else:
                        st.success(f"Found {len(ranked_df)} ranked candidates.")
                        
                        # Tabs for View
                        tab_table, tab_cards = st.tabs(["Table View", "Detailed Cards"])
                        
                        with tab_table:
                            display_cols = ['name', 'Match Score (%)', 'category', 'email', 'phone']
                            st.dataframe(
                                ranked_df[display_cols].style.highlight_max(subset=['Match Score (%)'], color='lightgreen'),
                                use_container_width=True
                            )
                            
                            # Export functionality
                            st.markdown("### Export Shortlist")
                            csv = ranked_df[display_cols].to_csv(index=False).encode('utf-8')
                            st.download_button(
                                label="Download as CSV",
                                data=csv,
                                file_name='shortlisted_candidates.csv',
                                mime='text/csv',
                            )
                            
                        with tab_cards:
                            for _, row in ranked_df.head(10).iterrows(): # Show top 10 cards
                                missing_skills = calculate_skill_gap(row['raw_text'], jd_text)
                                render_candidate_card(row.to_dict(), match_score=row['Match Score (%)'], missing_skills=missing_skills)
            elif not jd_text:
                st.info("Please enter a job description and click 'Rank Candidates'.")

# --- 4. Settings Page ---
elif page == "Settings":
    st.title("⚙️ Settings & Admin")
    
    st.subheader("Database Management")
    st.warning("Warning: This action cannot be undone.")
    if st.button("Clear Database"):
        clear_db()
        st.success("Database cleared successfully.")
        time.sleep(1)
        st.rerun()
        
    st.subheader("Model Management")
    st.markdown("Retrain the ML categorization model using the dummy dataset in `utils/model_trainer.py`.")
    if st.button("Retrain Model"):
        with st.spinner("Training model..."):
            try:
                import subprocess
                result = subprocess.run(["python", "utils/model_trainer.py"], capture_output=True, text=True)
                if result.returncode == 0:
                    st.success("Model retrained successfully!")
                    st.code(result.stdout)
                else:
                    st.error("Model training failed.")
                    st.code(result.stderr)
            except Exception as e:
                st.error(f"Error: {e}")
