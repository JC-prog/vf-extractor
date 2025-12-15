import streamlit as st
import os
import sys
import tempfile
from io import BytesIO
from pathlib import Path
import json
import pandas as pd

# 1. Directory Configuration
CURRENT_DIR = Path(__file__).resolve().parent
# Assuming single_extraction_view.py is in 'app/view/', so APP_DIR is 'app/'
APP_DIR = CURRENT_DIR.parent

# Key Directories
CONFIG_DIR = APP_DIR / 'config'
TEMPLATE_DIR = CONFIG_DIR / 'templates'
DATA_DIR = APP_DIR / 'data'

# Template Paths
HVF_TEMPLATE_PATH = TEMPLATE_DIR / 'hvf.json'
VRVF_TEMPLATE_PATH = TEMPLATE_DIR / 'vrvf.json'

# Map template selection names to their actual file paths
TEMPLATE_MAP = {
    "HVF": HVF_TEMPLATE_PATH,
    "VRVF": VRVF_TEMPLATE_PATH,
}

# For Development (Handling Module Imports)
try:
    # Assuming the project root is the parent of APP_DIR
    PROJECT_ROOT = APP_DIR.parent
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    from vfextractor.postprocessing.extract import Extractor
    from vfextractor.pipeline.pipeline import cropped_pipeline
except ModuleNotFoundError as e:
    st.error(f"Error loading module: {e}. Ensure 'vfextractor' is installed or the project root is correctly added to system path: {PROJECT_ROOT}")


# Function to handle data formatting for download
def format_data_for_download(data_objects, format_type):
    """Formats a list of extracted data objects into the specified file format."""
    if not data_objects:
        return "No data extracted.", "text/plain", "data.txt"

    # Assume data_objects is a list where each element is the result (dict/list) from one file extraction
    
    # Flatten the extracted data objects into a single list of records/dictionaries
    all_records = []
    for item in data_objects:
        if isinstance(item, list):
            all_records.extend(item)
        elif isinstance(item, dict):
            all_records.append(item)
        # Add handling for other data structures as needed (e.g., if it returns a specific class object)
        else:
            all_records.append({"data": str(item)}) # Fallback for non-standard data

    if format_type == "JSON":
        return json.dumps(all_records, indent=4), "application/json", "extracted_data.json"
    
    elif format_type == "CSV":
        try:
            df = pd.DataFrame(all_records)
            return df.to_csv(index=False), "text/csv", "extracted_data.csv"
        except Exception as e:
            st.error(f"Error converting data to CSV: {e}")
            # Fallback to text format on CSV failure
            return "\n".join(str(d) for d in data_objects), "text/plain", "extracted_data_error.txt"
        
    elif format_type == "TXT":
        # Simple string representation of all extracted data
        return "\n".join(str(d) for d in data_objects), "text/plain", "extracted_data.txt"

    return "Format not supported.", "text/plain", "data.txt"


def single_extraction_view():
    st.title("Single File Extractor")

    le_col, re_col = st.columns(2)

    # --- File Uploads ---
    with le_col:
        st.header("Left Eye - OS")
        uploaded_file_lehvf = st.file_uploader(
            "Upload **HVF** image file (PNG/JPG)",
            type=["png", "jpg", "jpeg"],
            key="lehvf_uploader"
        )
        if uploaded_file_lehvf is not None:
            st.success(f"File uploaded: {uploaded_file_lehvf.name}")
            st.image(uploaded_file_lehvf, caption=f"Preview: {uploaded_file_lehvf.name}")

    with re_col:
        st.header("Right Eye - OD")
        uploaded_file_rehvf = st.file_uploader(
            "Upload **HVF** image file (PNG/JPG)",
            type=["png", "jpg", "jpeg"],
            key="rehvf_uploader"
        )
        if uploaded_file_rehvf is not None:
            st.success(f"File uploaded: {uploaded_file_rehvf.name}")
            st.image(uploaded_file_rehvf, caption=f"Preview: {uploaded_file_rehvf.name}")
    
    # --- Function/Option Container ---
    function_container = st.container()
    
    with function_container:
        if 'extracted_text' not in st.session_state:
            st.session_state.extracted_text = "Text not extracted"
        if 'extracted_data_objects' not in st.session_state:
            st.session_state.extracted_data_objects = []

        # 2.1 Template selection
        template_options = list(TEMPLATE_MAP.keys())
        template_selection = st.selectbox(
            "Select Template: ",
            template_options
        )
        selected_template_path = TEMPLATE_MAP.get(template_selection)

        # 2.2 Export format selection
        output_format = st.selectbox(
            "Select export format",
            ("CSV", "TXT", "JSON")
        )

        pipeline_button = st.button("Run Pipeline", type="primary")

        if pipeline_button:
            if uploaded_file_lehvf is None and uploaded_file_rehvf is None:
                st.warning("Please upload at least one image file (HVF) for extraction.")
                st.session_state.extracted_text = "No file uploaded."
                st.session_state.extracted_data_objects = []
                return
            
            if selected_template_path is None:
                st.warning("Please select a valid template (HVF or VRVF) before running the pipeline.")
                st.session_state.extracted_text = "No valid template selected."
                st.session_state.extracted_data_objects = []
                return

            with st.spinner("Processing files and extracting data... This may take a moment."):
                extracted_data_list = [] # List for string summary
                extracted_data_objects = [] # List for structured data

                # Process files helper function
                def process_file(uploaded_file, eye_name, template_path):
                    if uploaded_file is None:
                        return

                    original_filename = Path(uploaded_file.name).stem
                    OUTPUT_DIR = DATA_DIR / original_filename

                    # Use tempfile.NamedTemporaryFile for automatic cleanup
                    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
                        uploaded_file.seek(0) 
                        tmp_file.write(uploaded_file.read())
                        tmp_file_path = tmp_file.name
                    
                    try:
                        data = cropped_pipeline(tmp_file_path, template_path, OUTPUT_DIR)
                        extracted_data_objects.append(data)
                        extracted_data_list.append(f"{eye_name} Data Extracted.")
                    except Exception as e:
                        st.error(f"Extraction failed for {eye_name}: {e}")
                    finally:
                        os.unlink(tmp_file_path)

                with st.spinner("Extraction Data from Left Eye..."):
                    # Process Left Eye
                    left_template_path = selected_template_path.with_stem(
                        selected_template_path.stem + "_left"
                    )
                    process_file(uploaded_file_lehvf, "Left Eye HVF", left_template_path)
                
                with st.spinner("Extracting Data from Right Eye..."):
                    # Process Right Eye
                    right_template_path = selected_template_path.with_stem(
                        selected_template_path.stem + "_right"
                    )
                    process_file(uploaded_file_rehvf, "Right Eye HVF", right_template_path)


                final_data_summary = "\n".join(extracted_data_list)
                if final_data_summary:
                    st.session_state.extracted_text = final_data_summary
                    st.session_state.extracted_data_objects = extracted_data_objects
                    st.success("Pipeline executed successfully!")
                else:
                    st.session_state.extracted_text = "Extraction failed or returned no data."
                    st.session_state.extracted_data_objects = []

        # --- Download Logic ---
        # The data for download is formatted using the selected output_format
        extracted_objects = st.session_state.get('extracted_data_objects', [])
        
        download_data, download_mime, download_filename = format_data_for_download(
            extracted_objects, 
            output_format
        )

        # Display the current state (helpful for debugging)
        st.write(f"Current extraction status: **{st.session_state.get('extracted_text', 'Text not extracted')}**")

        st.download_button(
            label=f"Download {output_format}",
            data=download_data,
            file_name=download_filename,
            mime=download_mime,
            icon=":material/download:",
            disabled=(not st.session_state.extracted_data_objects)
        )
        
# Run the main function
if __name__ == '__main__':
    single_extraction_view()