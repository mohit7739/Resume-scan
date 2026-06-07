import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def render_metric_card(title, value, icon=None):
    """Renders a styled metric card."""
    st.markdown(f"""
        <div style="background-color: var(--secondary-background-color); padding: 20px; border-radius: 10px; margin-bottom: 20px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h3 style="margin: 0; font-size: 1.2rem; color: var(--text-color);">{title}</h3>
            <h1 style="margin: 10px 0 0 0; font-size: 2.5rem; color: #4CAF50;">{value}</h1>
        </div>
    """, unsafe_allow_html=True)

def render_skill_pills(skills_list):
    """Renders a list of skills as styled pills."""
    html = '<div style="display: flex; flex-wrap: wrap; gap: 5px;">'
    for skill in skills_list:
        html += f'<span style="background-color: #e0e0e0; color: #333; padding: 3px 8px; border-radius: 12px; font-size: 0.8rem;">{skill}</span>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

def render_category_distribution(df):
    """Renders a pie chart of resume categories."""
    if df.empty or 'category' not in df.columns:
        st.info("No categorization data available.")
        return
        
    category_counts = df['category'].value_counts().reset_index()
    category_counts.columns = ['Category', 'Count']
    
    fig = px.pie(category_counts, values='Count', names='Category', hole=0.4,
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig, use_container_width=True)

def render_top_skills(df):
    """Renders a bar chart of the most common skills."""
    if df.empty or 'skills' not in df.columns:
        st.info("No skills data available.")
        return
        
    all_skills = []
    for skills_list in df['skills'].dropna():
        if isinstance(skills_list, list):
            all_skills.extend(skills_list)
            
    if not all_skills:
        st.info("No skills extracted yet.")
        return
        
    skills_series = pd.Series(all_skills)
    top_skills = skills_series.value_counts().head(10).reset_index()
    top_skills.columns = ['Skill', 'Count']
    
    fig = px.bar(top_skills, x='Count', y='Skill', orientation='h',
                 color='Count', color_continuous_scale='Blues')
    fig.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig, use_container_width=True)

def render_candidate_card(candidate, match_score=None, missing_skills=None):
    """Renders a detailed card for a single candidate."""
    with st.container():
        st.markdown(f"### {candidate.get('name', 'Unknown')}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Email:** {candidate.get('email', 'N/A')}")
            st.write(f"**Phone:** {candidate.get('phone', 'N/A')}")
        with col2:
            st.write(f"**Category:** {candidate.get('category', 'N/A')}")
            if match_score is not None:
                st.write(f"**Match Score:** :green[{match_score}%]")
                
        st.write("**Skills Extracted:**")
        render_skill_pills(candidate.get('skills', []))
        
        if missing_skills:
            st.write("**Missing from JD:**")
            st.markdown(f"<span style='color: #e53935; font-size: 0.9rem;'>{', '.join(missing_skills)}</span>", unsafe_allow_html=True)
            
        st.divider()
