import pandas as pd
import numpy as np
from typing import Dict, List

def calculate_pace_adjustment(grade: float) -> float:
    """Calculate pace adjustment factor based on grade."""
    if grade > 0:  # Uphill
        # Reduce the impact of grade on pace
        return 1 + (grade * 0.075)  # Reduced from 0.1
    else:  # Downhill
        # Reduce the impact of downhill
        return 1 + (abs(grade) * 0.025)  # Reduced from 0.05

def calculate_time_estimates(track_data: Dict, target_time: float, split_interval: float = 5.0) -> List[Dict]:
    """Calculate time estimates for given distance intervals."""
    df = track_data['data']
    total_distance = track_data['total_distance']

    # Ensure we have data
    if len(df) == 0:
        return []

    # Calculate base pace (minutes per km)
    base_pace = (target_time * 60) / total_distance

    # Create checkpoints at specified intervals
    checkpoints = []
    current_distance = 0
    accumulated_time = 0

    # First pass: calculate raw adjusted times
    raw_checkpoints = []
    total_adjusted_time = 0

    while current_distance < total_distance:
        next_distance = min(current_distance + split_interval, total_distance)
        segment = df[(df['distance'] >= current_distance) & 
                    (df['distance'] <= next_distance)]

        if len(segment) == 0:
            break

        segment_distance = next_distance - current_distance
        segment_time = 0

        # Calculate segment time with grade adjustments
        for _, row in segment.iterrows():
            adjustment = calculate_pace_adjustment(row['grade'])
            segment_time += base_pace * adjustment * (segment_distance/len(segment))

        total_adjusted_time += segment_time
        raw_checkpoints.append({
            'distance': next_distance,
            'time': segment_time,
            'elevation': segment['elevation'].iloc[-1] if not segment.empty else 0
        })
        current_distance = next_distance

    # Second pass: normalize times to match target
    scale_factor = (target_time * 60) / total_adjusted_time
    accumulated_time = 0

    for checkpoint in raw_checkpoints:
        adjusted_time = checkpoint['time'] * scale_factor
        accumulated_time += adjusted_time

        checkpoints.append({
            'distance': checkpoint['distance'],
            'estimated_time': accumulated_time,
            'split_time': adjusted_time,
            'elevation': checkpoint['elevation']
        })

    return checkpoints