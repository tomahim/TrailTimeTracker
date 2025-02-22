
import gpxpy
import pandas as pd
import numpy as np
from typing import Dict, Any

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points using the Haversine formula."""
    R = 6371  # Earth's radius in kilometers

    # Ensure all inputs are float
    lat1, lon1, lat2, lon2 = float(lat1), float(lon1), float(lat2), float(lon2)
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    return R * c

def process_gpx_file(gpx_file_path: str) -> Dict[str, Any]:
    """Process GPX file and return track data."""
    try:
        with open(gpx_file_path, 'r') as gpx_file:
            gpx = gpxpy.parse(gpx_file)

        data_points = []
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    data_points.append({
                        'latitude': float(point.latitude),
                        'longitude': float(point.longitude),
                        'elevation': float(point.elevation if point.elevation is not None else 0.0),
                        'time': point.time
                    })

        if not data_points:
            raise ValueError("No valid data points found in GPX file")

        df = pd.DataFrame(data_points)
        
        # Initialize distance column with float values
        df['distance'] = pd.Series(dtype=float)
        df.loc[0, 'distance'] = 0.0
        
        # Calculate distances
        for i in range(1, len(df)):
            df.loc[i, 'distance'] = df.loc[i-1, 'distance'] + calculate_distance(
                df.loc[i-1, 'latitude'],
                df.loc[i-1, 'longitude'],
                df.loc[i, 'latitude'],
                df.loc[i, 'longitude']
            )

        # Calculate grade
        df['grade'] = pd.Series(dtype=float)
        df.loc[0, 'grade'] = 0.0
        
        for i in range(1, len(df)):
            distance_delta = (df.loc[i, 'distance'] - df.loc[i-1, 'distance']) * 1000  # Convert to meters
            if distance_delta > 0:
                elevation_delta = df.loc[i, 'elevation'] - df.loc[i-1, 'elevation']
                df.loc[i, 'grade'] = (elevation_delta / distance_delta) * 100
            else:
                df.loc[i, 'grade'] = 0.0

        # Calculate elevation changes
        elevation_diff = df['elevation'].diff()
        elevation_gain = elevation_diff[elevation_diff > 0].sum()
        elevation_loss = abs(elevation_diff[elevation_diff < 0].sum())

        return {
            'data': df,
            'total_distance': float(df['distance'].max()),
            'total_elevation_gain': float(elevation_gain if not pd.isna(elevation_gain) else 0.0),
            'total_elevation_loss': float(elevation_loss if not pd.isna(elevation_loss) else 0.0),
            'max_elevation': float(df['elevation'].max()),
            'min_elevation': float(df['elevation'].min()),
        }

    except Exception as e:
        print(f"Error processing GPX file: {str(e)}")
        raise
