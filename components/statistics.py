import streamlit as st
from typing import Dict, List

def format_time(minutes: float) -> str:
    """Convert minutes to HH:MM format."""
    hours = int(minutes // 60)
    mins = int(minutes % 60)
    return f"{hours:02d}:{mins:02d}"

def display_statistics(track_data: Dict, time_estimates: List[Dict]):
    """Display trail statistics and time estimates."""
    st.header("Trail Statistics")
    
    # Display basic statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Total Distance",
            f"{track_data['total_distance']:.1f} km"
        )
    
    with col2:
        st.metric(
            "Total Elevation Gain",
            f"{track_data['total_elevation_gain']:.0f} m"
        )
    
    with col3:
        st.metric(
            "Total Elevation Loss",
            f"{track_data['total_elevation_loss']:.0f} m"
        )

    # Display time estimates
    st.subheader("Estimated Times at 5km Intervals")
    
    # Create a table for time estimates
    data = []
    for checkpoint in time_estimates:
        data.append({
            "Distance (km)": f"{checkpoint['distance']:.1f}",
            "Elevation (m)": f"{checkpoint['elevation']:.0f}",
            "Split Time": format_time(checkpoint['split_time']),
            "Cumulative Time": format_time(checkpoint['estimated_time'])
        })
    
    st.table(data)
