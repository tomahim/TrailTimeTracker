import pandas as pd
import numpy as np
from typing import Dict, List

def calculate_pace_adjustment(grade: float) -> float:
    """Calculate pace adjustment factor based on grade."""
    try:
        grade = float(grade)  # Ensure grade is float
        if grade > 0:  # Uphill
            return 1 + (grade * 0.075)  # Reduced from 0.1
        else:  # Downhill
            return 1 + (abs(grade) * 0.025)  # Reduced from 0.05
    except (TypeError, ValueError):
        return 1.0  # Default to no adjustment if conversion fails

def calculate_time_estimates(track_data: Dict, target_time: float, split_interval: float = 5.0) -> List[Dict]:
    """Calculate time estimates for given distance intervals."""
    try:
        df = track_data.get('data')
        if df is None or len(df) == 0:
            return []

        total_distance = float(track_data.get('total_distance', 0))
        if total_distance <= 0:
            return []

        # Convert inputs to proper types
        target_time = float(target_time)
        split_interval = float(split_interval)

        # Calculate base pace (minutes per km)
        base_pace = (target_time * 60) / total_distance

        # Create checkpoints at specified intervals
        checkpoints = []
        current_distance = 0.0
        accumulated_time = 0.0

        # First pass: calculate raw adjusted times
        raw_checkpoints = []
        total_adjusted_time = 0.0

        while current_distance < total_distance:
            next_distance = min(current_distance + split_interval, total_distance)
            segment = df[(df['distance'] >= current_distance) & 
                        (df['distance'] <= next_distance)]

            if len(segment) == 0:
                break

            segment_distance = next_distance - current_distance
            segment_time = 0.0

            # Calculate segment time with grade adjustments
            for _, row in segment.iterrows():
                adjustment = calculate_pace_adjustment(row.get('grade', 0))
                point_time = base_pace * adjustment * (segment_distance/len(segment))
                segment_time += float(point_time)

            total_adjusted_time += segment_time
            raw_checkpoints.append({
                'distance': float(next_distance),
                'time': float(segment_time),
                'elevation': float(segment['elevation'].iloc[-1]) if not segment.empty else 0.0
            })
            current_distance = next_distance

        # Second pass: normalize times to match target
        if total_adjusted_time > 0:
            scale_factor = (target_time * 60) / total_adjusted_time
            accumulated_time = 0.0

            for checkpoint in raw_checkpoints:
                adjusted_time = checkpoint['time'] * scale_factor
                accumulated_time += adjusted_time

                checkpoints.append({
                    'distance': float(checkpoint['distance']),
                    'estimated_time': float(accumulated_time),
                    'split_time': float(adjusted_time),
                    'elevation': float(checkpoint['elevation'])
                })

        return checkpoints
    except Exception as e:
        print(f"Error in time calculation: {str(e)}")
        return []