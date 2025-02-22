import streamlit as st
import plotly.graph_objects as go
from typing import Dict, List

def format_time(minutes: float) -> str:
    """Convert minutes to HH:MM format."""
    hours = int(minutes // 60)
    mins = int(minutes % 60)
    return f"{hours:02d}:{mins:02d}"

def display_elevation_profile(track_data: Dict, time_estimates: List[Dict] = None):
    """Display elevation profile using Plotly."""
    df = track_data['data']

    fig = go.Figure()

    # Create hover text with time estimates
    hover_text = []
    for _, row in df.iterrows():
        # Find closest time estimate
        if time_estimates:
            closest_estimate = min(time_estimates, 
                                 key=lambda x: abs(x['distance'] - row['distance']))
            time_text = f"Est. Time: {format_time(closest_estimate['estimated_time'])}"
        else:
            time_text = ""

        hover_text.append(
            f"Distance: {row['distance']:.1f} km<br>"
            f"Elevation: {row['elevation']:.0f} m<br>"
            f"{time_text}"
        )

    # Add elevation profile
    fig.add_trace(go.Scatter(
        x=df['distance'],
        y=df['elevation'],
        mode='lines',
        name='Elevation',
        fill='tozeroy',
        line=dict(color='rgb(73, 116, 165)'),
        fillcolor='rgba(73, 116, 165, 0.2)',
        hovertext=hover_text,
        hoverinfo='text'
    ))

    # Update layout
    fig.update_layout(
        title='Elevation Profile',
        xaxis_title='Distance (km)',
        yaxis_title='Elevation (m)',
        hovermode='closest',
        showlegend=False,
        height=400,
        margin=dict(l=0, r=0, t=30, b=0)
    )

    # Add 5km interval markers
    distance = 0
    while distance <= df['distance'].max():
        fig.add_vline(
            x=distance,
            line_dash="dash",
            line_color="rgba(0, 0, 0, 0.3)"
        )
        distance += 5

    st.plotly_chart(fig, use_container_width=True)