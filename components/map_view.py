import streamlit as st
import folium
from streamlit_folium import folium_static
from typing import Dict

def display_map(track_data: Dict):
    """Display the trail map using Folium."""
    df = track_data['data']
    
    # Create the map centered on the first point
    m = folium.Map(
        location=[df['latitude'].iloc[0], df['longitude'].iloc[0]],
        zoom_start=12,
        tiles='OpenStreetMap'
    )
    
    # Create the trail line
    points = [[row['latitude'], row['longitude']] for _, row in df.iterrows()]
    folium.PolyLine(
        points,
        weight=3,
        color='red',
        opacity=0.8
    ).add_to(m)
    
    # Add markers every 5km
    distance = 0
    for _, row in df.iterrows():
        if row['distance'] >= distance:
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=6,
                color='blue',
                popup=f'{distance:.1f}km',
                fill=True
            ).add_to(m)
            distance += 5

    # Display the map
    st.subheader("Trail Map")
    folium_static(m)
