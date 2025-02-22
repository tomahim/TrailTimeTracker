import streamlit as st
import tempfile
from utils.gpx_processor import process_gpx_file
from utils.time_calculator import calculate_time_estimates
from components.map_view import display_map
from components.elevation_profile import display_elevation_profile
from components.statistics import display_statistics

st.set_page_config(
    page_title="Trail Running Analysis",
    page_icon="🏃",
    layout="wide"
)

def main():
    st.title("🏃 Trail Running Analysis Tool")

    # File upload section
    st.header("Upload your GPX file")
    uploaded_file = st.file_uploader(
        "Drag and drop your GPX file here",
        type=['gpx'],
        help="Upload a GPX file containing your trail route"
    )

    if uploaded_file is not None:
        try:
            # Save uploaded file to temp location
            with tempfile.NamedTemporaryFile(delete=False, suffix='.gpx') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                gpx_file_path = tmp_file.name

            # Process GPX file
            track_data = process_gpx_file(gpx_file_path)

            # Get target time input
            target_time = st.number_input(
                "Enter your target time (hours)",
                min_value=0.1,
                max_value=48.0,
                value=4.0,
                step=0.1
            )

            # Calculate time estimates
            time_estimates = calculate_time_estimates(track_data, target_time)

            # Display visualizations in columns
            col1, col2 = st.columns(2)

            with col1:
                # Display map
                display_map(track_data)

            with col2:
                # Display elevation profile with time estimates
                display_elevation_profile(track_data, time_estimates)

            # Display statistics
            display_statistics(track_data, time_estimates)

        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

if __name__ == "__main__":
    main()