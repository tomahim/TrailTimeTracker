import gpxpy
import pandas as pd
import numpy as np
from typing import Dict, Any

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points using the Haversine formula."""
    R = 6371  # Earth's radius in kilometers

    lat1, lon1, lat2, lon2 = map(np.radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    return float(R * c)

def process_gpx_file(gpx_file_path: str) -> Dict[str, Any]:
    """Process GPX file and return track data."""
    try:
        with open(gpx_file_path, 'r') as gpx_file:
            gpx = gpxpy.parse(gpx_file)

        data_points = []

        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    # Ensure all values are proper types
                    try:
                        data_point = {
                            'latitude': float(point.latitude),
                            'longitude': float(point.longitude),
                            'elevation': float(point.elevation if point.elevation is not None else 0.0),
                            'time': point.time
                        }
                        data_points.append(data_point)
                    except (TypeError, ValueError) as e:
                        print(f"Error processing point: {e}")
                        continue

        if not data_points:
            raise ValueError("No valid data points found in GPX file")

        # Convert to DataFrame
        df = pd.DataFrame(data_points)

        # Calculate cumulative distance
        df['distance'] = 0.0
        for i in range(1, len(df)):
            try:
                df.loc[i, 'distance'] = float(df.loc[i-1, 'distance']) + calculate_distance(
                    df.loc[i-1, 'latitude'],
                    df.loc[i-1, 'longitude'],
                    df.loc[i, 'latitude'],
                    df.loc[i, 'longitude']
                )
            except (TypeError, ValueError) as e:
                print(f"Error calculating distance at index {i}: {e}")
                df.loc[i, 'distance'] = df.loc[i-1, 'distance']

        # Calculate grade (slope)
        df['grade'] = 0.0
        for i in range(1, len(df)):
            try:
                distance = (float(df.loc[i, 'distance']) - float(df.loc[i-1, 'distance'])) * 1000  # Convert to meters
                if distance > 0:
                    elevation_change = float(df.loc[i, 'elevation']) - float(df.loc[i-1, 'elevation'])
                    df.loc[i, 'grade'] = float((elevation_change / distance) * 100)
            except (TypeError, ValueError) as e:
                print(f"Error calculating grade at index {i}: {e}")
                df.loc[i, 'grade'] = 0.0

        # Ensure all numeric columns are float type
        numeric_columns = ['latitude', 'longitude', 'elevation', 'distance', 'grade']
        for col in numeric_columns:
            df[col] = df[col].astype(float)

        return {
            'data': df,
            'total_distance': float(df['distance'].max()),
            'total_elevation_gain': float(df['elevation'].diff()[df['elevation'].diff() > 0].sum()),
            'total_elevation_loss': float(abs(df['elevation'].diff()[df['elevation'].diff() < 0].sum())),
            'max_elevation': float(df['elevation'].max()),
            'min_elevation': float(df['elevation'].min()),
        }

    except Exception as e:
        print(f"Error processing GPX file: {str(e)}")
        raise