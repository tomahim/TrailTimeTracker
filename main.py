import streamlit as st
import tempfile
from utils.gpx_processor import process_gpx_file
from utils.time_calculator import calculate_time_estimates
from components.map_view import display_map
from components.elevation_profile import display_elevation_profile
from components.statistics import display_statistics
from models.database import get_db, Analysis
import io
import traceback

st.set_page_config(page_title="Trail Running Analysis",
                   page_icon="🏃",
                   layout="wide")


def format_time(minutes: float) -> str:
    """Convert minutes to formatted time string."""
    hours = int(minutes // 60)
    mins = int(minutes % 60)
    return f"{hours}h{mins:02d}"


def save_analysis(gpx_data: bytes, name: str, target_time: float,
                  split_interval: float):
    """Save analysis to database."""
    db = next(get_db())
    analysis = Analysis(name=name,
                        gpx_file=gpx_data,
                        target_time=target_time,
                        split_interval=split_interval)
    db.add(analysis)
    db.commit()
    return analysis.id


def main():
    st.title("🏃 Trail Running Analysis Tool")

    # Add a home button
    if st.button("← Back to Home"):
        st.switch_page("pages/home.py")

    # Check if we're loading a saved analysis
    analysis_id = st.session_state.get('analysis_id', None)

    if analysis_id:
        db = next(get_db())
        analysis = db.query(Analysis).filter(
            Analysis.id == analysis_id).first()
        if analysis:
            with tempfile.NamedTemporaryFile(delete=False,
                                             suffix='.gpx') as tmp_file:
                tmp_file.write(analysis.gpx_file)
                gpx_file_path = tmp_file.name
            track_data = process_gpx_file(gpx_file_path)
            uploaded_file = None
            target_minutes = float(analysis.target_time)  # Convert to float
            split_interval = float(analysis.split_interval)  # Convert to float
        else:
            st.error("Analysis not found")
            return
    else:
        st.header("Upload your GPX file")
        uploaded_file = st.file_uploader(
            "Drag and drop your GPX file here",
            type=['gpx'],
            help="Upload a GPX file containing your trail route")

        if uploaded_file is None:
            return

        with tempfile.NamedTemporaryFile(delete=False,
                                         suffix='.gpx') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            gpx_file_path = tmp_file.name

        track_data = process_gpx_file(gpx_file_path)
        target_minutes = 240.0  # Explicitly set as float
        split_interval = 5.0  # Explicitly set as float

    try:
        time_col1, time_col2, time_col3 = st.columns([2, 2, 1])

        with time_col1:
            target_minutes = st.slider(
                f"Target time ({format_time(240)})",
                min_value=30,
                max_value=48 * 60,  
                value=int(target_minutes),
                step=15)
            target_time = target_minutes / 60.0  # Ensure float division

        with time_col2:
            split_interval = float(
                st.selectbox(  # Convert selectbox value to float
                    "Split interval",
                    options=[1, 5, 10, 15, 20],
                    index=1 if split_interval == 5 else 0,
                    format_func=lambda x: f"{x}km",
                    help="Choose the distance interval for time estimates"))

        with time_col3:
            st.metric("Selected Time", format_time(target_minutes))

        if not analysis_id and uploaded_file:
            save_col1, save_col2 = st.columns([2, 1])
            with save_col1:
                analysis_name = st.text_input("Analysis name",
                                              value="My Trail Run")
            with save_col2:
                if st.button("Save Analysis"):
                    save_analysis(
                        uploaded_file.getvalue(),
                        analysis_name,
                        float(target_minutes),  # Ensure float
                        float(split_interval)  # Ensure float
                    )
                    st.success("Analysis saved!")

        # Calculate time estimates with explicit float conversion
        time_estimates = calculate_time_estimates(track_data,
                                                  float(target_time),
                                                  float(split_interval))

        col1, col2 = st.columns(2)
        with col1:
            display_map(track_data, float(split_interval))
        with col2:
            display_elevation_profile(track_data, time_estimates)

        display_statistics(track_data, time_estimates)

    except Exception as e:
        traceback = e.__traceback__
        while traceback:
            st.error("{}: {}".format(traceback.tb_frame.f_code.co_filename,
                                     traceback.tb_lineno))
            traceback = traceback.tb_next


if __name__ == "__main__":
    main()
