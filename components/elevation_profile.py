import streamlit as st
import plotly.graph_objects as go
from typing import Dict

def display_elevation_profile(track_data: Dict):
    """Display elevation profile using Plotly."""
    df = track_data['data']
    
    fig = go.Figure()
    
    # Add elevation profile
    fig.add_trace(go.Scatter(
        x=df['distance'],
        y=df['elevation'],
        mode='lines',
        name='Elevation',
        fill='tozeroy',
        line=dict(color='rgb(73, 116, 165)'),
        fillcolor='rgba(73, 116, 165, 0.2)'
    ))
    
    # Update layout
    fig.update_layout(
        title='Elevation Profile',
        xaxis_title='Distance (km)',
        yaxis_title='Elevation (m)',
        hovermode='x',
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
