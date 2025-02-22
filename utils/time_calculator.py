import pandas as pd
import numpy as np
from typing import Dict, List

def calculate_pace_adjustment(grade: float) -> float:
    """Calculate pace adjustment factor based on grade."""
    if grade > 0:  # Uphill
        return 1 + (grade * 0.1)
    else:  # Downhill
        return 1 + (abs(grade) * 0.05)

def calculate_time_estimates(track_data: Dict, target_time: float) -> List[Dict]:
    """Calculate time estimates for 5km intervals."""
    df = track_data['data']
    total_distance = track_data['total_distance']

    # Ensure we have data
    if len(df) == 0:
        return []

    # Calculate base pace (minutes per km)
    base_pace = (target_time * 60) / total_distance

    # Create 5km checkpoints
    checkpoints = []
    current_distance = 0
    accumulated_time = 0

    while current_distance < total_distance:
        next_distance = min(current_distance + 5, total_distance)

        # Get segment data
        segment = df[(df['distance'] >= current_distance) & 
                    (df['distance'] <= next_distance)]

        # Skip if segment is empty
        if len(segment) == 0:
            break

        # Calculate adjusted time for segment
        segment_time = 0
        segment_distance = next_distance - current_distance

        for _, row in segment.iterrows():
            adjustment = calculate_pace_adjustment(row['grade'])
            # Calculate time proportionally based on actual segment distance
            segment_time += base_pace * adjustment * (segment_distance/len(segment))

        accumulated_time += segment_time

        # Use the last available elevation for this segment
        current_elevation = segment['elevation'].iloc[-1] if not segment.empty else 0

        checkpoints.append({
            'distance': next_distance,
            'estimated_time': accumulated_time,
            'split_time': segment_time,
            'elevation': current_elevation
        })

        current_distance = next_distance

    return checkpoints