import streamlit as st
from models.database import get_db, Analysis
import io
from datetime import datetime

def format_time(minutes: float) -> str:
    """Convert minutes to formatted time string."""
    hours = int(minutes // 60)
    mins = int(minutes % 60)
    return f"{hours}h{mins:02d}"

def list_analyses():
    st.title("🏃 Trail Running Analyses")
    
    # Create New Analysis button
    if st.button("Create New Analysis", type="primary"):
        st.switch_page("main.py")
    
    st.header("Saved Analyses")
    
    # Get all analyses from database
    db = next(get_db())
    analyses = db.query(Analysis).order_by(Analysis.created_at.desc()).all()
    
    if not analyses:
        st.info("No saved analyses yet. Create your first analysis!")
        return
    
    # Display analyses in a grid
    cols = st.columns(3)
    for idx, analysis in enumerate(analyses):
        with cols[idx % 3]:
            with st.container(border=True):
                st.subheader(analysis.name)
                st.text(f"Target Time: {format_time(analysis.target_time)}")
                st.text(f"Split Interval: {analysis.split_interval}km")
                st.text(f"Created: {analysis.created_at.strftime('%Y-%m-%d')}")
                
                # View Analysis button
                if st.button("View Analysis", key=f"view_{analysis.id}"):
                    # Store analysis ID in session state
                    st.session_state.analysis_id = analysis.id
                    st.switch_page("main.py")

if __name__ == "__main__":
    list_analyses()
