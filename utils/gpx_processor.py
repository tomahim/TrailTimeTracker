import gpxpy
import pandas as pd
import numpy as np
from typing import Dict, Any

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points using the Haversine formula."""
    R = 6371  # Earth's radius in kilometers
    
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    return R * c

def process_gpx_file(gpx_file_path: str) -> Dict[str, Any]:
    """Process GPX file and return track data."""
    with open(gpx_file_path, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    data_points = []
    
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                data_points.append({
                    'latitude': point.latitude,
                    'longitude': point.longitude,
                    'elevation': point.elevation,
                    'time': point.time
                })

    # Convert to DataFrame
    df = pd.DataFrame(data_points)
    
    # Calculate cumulative distance
    df['distance'] = 0.0
    for i in range(1, len(df)):
        df.loc[i, 'distance'] = df.loc[i-1, 'distance'] + calculate_distance(
            df.loc[i-1, 'latitude'],
            df.loc[i-1, 'longitude'],
            df.loc[i, 'latitude'],
            df.loc[i, 'longitude']
        )

    # Calculate grade (slope)
    df['grade'] = 0.0
    for i in range(1, len(df)):
        distance = (df.loc[i, 'distance'] - df.loc[i-1, 'distance']) * 1000  # Convert to meters
        if distance > 0:
            elevation_change = df.loc[i, 'elevation'] - df.loc[i-1, 'elevation']
            df.loc[i, 'grade'] = (elevation_change / distance) * 100

    return {
        'data': df,
        'total_distance': df['distance'].max(),
        'total_elevation_gain': df['elevation'].diff()[df['elevation'].diff() > 0].sum(),
        'total_elevation_loss': abs(df['elevation'].diff()[df['elevation'].diff() < 0].sum()),
        'max_elevation': df['elevation'].max(),
        'min_elevation': df['elevation'].min(),
    }
