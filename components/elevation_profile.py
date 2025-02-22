import streamlit as st
import plotly.graph_objects as go
from typing import Dict, List
import numpy as np
from scipy.interpolate import interp1d

def format_time(minutes: float) -> str:
    """Convert minutes to HH:MM format."""
    hours = int(minutes // 60)
    mins = int(minutes % 60)
    return f"{hours:02d}h{mins:02d}"

def interpolate_times(time_estimates: List[Dict], distances: np.ndarray) -> np.ndarray:
    """Interpolate times for all points based on split estimates."""
    split_distances = [est['distance'] for est in time_estimates]
    split_times = [est['estimated_time'] for est in time_estimates]

    # Create interpolation function
    f = interp1d(split_distances, split_times, kind='linear', fill_value='extrapolate')

    # Interpolate times for all distances
    return f(distances)

def display_elevation_profile(track_data: Dict, time_estimates: List[Dict] = None):
    """Display elevation profile using Plotly."""
    df = track_data['data']

    fig = go.Figure()

    # Interpolate times for all points if time estimates are provided
    if time_estimates:
        interpolated_times = interpolate_times(time_estimates, df['distance'].values)

    # Create hover text with time estimates
    hover_text = []
    for idx, row in df.iterrows():
        time_text = (f"Est. Time: {format_time(interpolated_times[idx])}"
                    if time_estimates else "")

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

    # Add interval markers
    if time_estimates:
        for estimate in time_estimates:
            fig.add_vline(
                x=estimate['distance'],
                line_dash="dash",
                line_color="rgba(0, 0, 0, 0.3)"
            )

    st.plotly_chart(fig, use_container_width=True)