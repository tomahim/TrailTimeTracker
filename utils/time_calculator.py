import pandas as pd
import numpy as np
from typing import List, Dict

def calculate_pace_adjustment(grade: float) -> float:
    """Calculate pace adjustment factor based on grade."""
    if grade > 0:
        return 1.0 + (grade * 0.1)  # Slower on uphills
    else:
        return 1.0 + (abs(grade) * 0.05)  # Slightly faster on downhills

def calculate_time_estimates(track_data: Dict, target_time: float, split_interval: float) -> List[Dict]:
    """Calculate estimated times for track segments."""
    try:
        df = track_data['data']
        total_distance = float(track_data['total_distance'])

        if total_distance <= 0:
            return []

        # Base pace in minutes per kilometer
        base_pace = (target_time * 60) / total_distance

        checkpoints = []
        current_distance = 0.0

        while current_distance < total_distance:
            next_distance = min(current_distance + split_interval, total_distance)

            # Get segment data
            mask = (df['distance'] >= current_distance) & (df['distance'] <= next_distance)
            segment = df[mask].copy()

            if segment.empty:
                continue

            segment_distance = next_distance - current_distance
            segment_time = 0.0

            # Calculate time for this segment
            for _, row in segment.iterrows():
                grade = float(row.get('grade', 0))
                adjustment = calculate_pace_adjustment(grade)
                point_time = base_pace * adjustment * (segment_distance/len(segment))
                segment_time += point_time

            checkpoints.append({
                'distance': float(next_distance),
                'estimated_time': float(sum(c['split_time'] for c in checkpoints if 'split_time' in c) + segment_time),
                'split_time': float(segment_time),
                'elevation': float(segment['elevation'].iloc[-1]) if not segment.empty else 0.0
            })

            current_distance = next_distance

        return checkpoints

    except Exception as e:
        print(f"Error in time calculation: {str(e)}")
        return []