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
    PROJECT_ROOT = APP_DIR.parent
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    from vfextractor.preprocessing.converter import convert_from_path
    from vfextractor.postprocessing.extract import Extractor
    from vfextractor.pipeline.pipeline import cropped_pipeline
    
except ModuleNotFoundError as e:
    st.error(f"Error loading module: {e}. Ensure 'vfextractor' is installed or the project root is correctly added to system path: {PROJECT_ROOT}")


# Function to handle data formatting for download
def format_data_for_download(data_objects, format_type):
    """Formats a list of extracted data objects into the specified file format."""
    if not data_objects:
        return "No data extracted.", "text/plain", "data.txt"

    all_records = []
    for item in data_objects:
        if isinstance(item, list):
            all_records.extend(item)
        elif isinstance(item, dict):
            all_records.append(item)
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
            return "\n".join(str(d) for d in data_objects), "text/plain", "extracted_data_error.txt"
        
    elif format_type == "TXT":
        return "\n".join(str(d) for d in data_objects), "text/plain", "extracted_data.txt"

    return "Format not supported.", "text/plain", "data.txt"

# Function to process files
def process_file(uploaded_file, eye_name, template_path, extracted_data_objects, extracted_data_list):
    """
    Processes an uploaded file. If it's a PDF, converts it to PNG image(s) 
    in a temporary location before running the cropped_pipeline.
    Updates the provided extracted_data_objects and extracted_data_list in place.
    """
    if uploaded_file is None:
        return

    original_filename_stem = Path(uploaded_file.name).stem
    file_suffix = Path(uploaded_file.name).suffix.lower()
    OUTPUT_DIR = DATA_DIR / 'output' / original_filename_stem
    
    files_to_process = []
    temp_files_to_clean = [] 

    # 1. Handle File Upload and Temporary Storage
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_suffix) as tmp_file:
        uploaded_file.seek(0) 
        tmp_file.write(uploaded_file.read())
        uploaded_file_path = tmp_file.name
        temp_files_to_clean.append(uploaded_file_path)

    # 2. Check for PDF and Convert if necessary
    if file_suffix == '.pdf':
        try:
            pdf_pages = convert_from_path(uploaded_file_path)
            
            for i, img in enumerate(pdf_pages):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as png_tmp_file:
                    png_output_path = png_tmp_file.name
                
                img.save(png_output_path, "PNG")
                
                files_to_process.append(png_output_path)
                temp_files_to_clean.append(png_output_path)
                
            st.info(f"PDF converted to {len(files_to_process)} PNG file(s) for {eye_name}.")
            
        except Exception as e:
            st.error(f"PDF conversion failed for {eye_name}: {e}")
            files_to_process = [] 
            
    else:
        files_to_process.append(uploaded_file_path)

    # 3. Process the file(s)
    
    if files_to_process:
        for tmp_file_path in files_to_process:
            try:
                # Assuming cropped_pipeline handles a single file path and returns data
                data = cropped_pipeline(tmp_file_path, template_path, OUTPUT_DIR)
                
                # --- CRITICAL FIX: Append to the passed-in lists ---
                extracted_data_objects.append(data) 
                
                if file_suffix == '.pdf':
                    extracted_data_list.append(f"{eye_name} Data Extracted (Page {files_to_process.index(tmp_file_path) + 1}).")
                else:
                    extracted_data_list.append(f"{eye_name} Data Extracted.")
                    
            except Exception as e:
                st.error(f"Extraction failed for {eye_name} ({Path(tmp_file_path).name}): {e}")

    # 4. Cleanup
    for file_to_unlink in temp_files_to_clean:
        try:
            os.unlink(file_to_unlink)
        except OSError as e:
            print(f"Error cleaning up temporary file {file_to_unlink}: {e}")


def single_extraction_view():
    st.title("Single File Extractor")

    le_col, re_col = st.columns(2)

    # --- File Uploads ---
    with le_col:
        st.header("Left Eye - OS")
        # NOTE: Allowing PDF upload since process_file handles conversion
        uploaded_file_lehvf = st.file_uploader(
            "Upload **HVF** image/PDF file",
            type=["png", "jpg", "jpeg", "pdf"],
            key="lehvf_uploader"
        )
        if uploaded_file_lehvf is not None:
            st.success(f"File uploaded: {uploaded_file_lehvf.name}")
            # Do not display PDF preview directly, as Streamlit cannot preview arbitrary PDFs
            if uploaded_file_lehvf.type != "application/pdf":
                st.image(uploaded_file_lehvf, caption=f"Preview: {uploaded_file_lehvf.name}")


    with re_col:
        st.header("Right Eye - OD")
        uploaded_file_rehvf = st.file_uploader(
            "Upload **HVF** image/PDF file",
            type=["png", "jpg", "jpeg", "pdf"],
            key="rehvf_uploader"
        )
        if uploaded_file_rehvf is not None:
            st.success(f"File uploaded: {uploaded_file_rehvf.name}")
            if uploaded_file_rehvf.type != "application/pdf":
                st.image(uploaded_file_rehvf, caption=f"Preview: {uploaded_file_rehvf.name}")
    
    # --- Function/Option Container ---
    function_container = st.container()
    
    with function_container:
        if 'extracted_text' not in st.session_state:
            st.session_state.extracted_text = "Text not extracted"
        if 'extracted_data_objects' not in st.session_state:
            st.session_state.extracted_data_objects = []

        # Template selection
        template_options = list(TEMPLATE_MAP.keys())
        template_selection = st.selectbox(
            "Select Template: ",
            template_options
        )
        selected_template_path = TEMPLATE_MAP.get(template_selection)

        pipeline_button = st.button("Run Pipeline", type="primary")

        if pipeline_button:
            if uploaded_file_lehvf is None and uploaded_file_rehvf is None:
                st.warning("Please upload at least one file (HVF) for extraction.")
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

                with st.spinner("Extraction Data from Left Eye..."):
                    # Process Left Eye
                    left_template_path = selected_template_path.with_stem(
                        selected_template_path.stem + "_left"
                    )
                    process_file(uploaded_file_lehvf, "Left Eye HVF", left_template_path, extracted_data_objects, extracted_data_list)
                
                with st.spinner("Extracting Data from Right Eye..."):
                    # Process Right Eye
                    right_template_path = selected_template_path.with_stem(
                        selected_template_path.stem + "_right"
                    )
                    process_file(uploaded_file_rehvf, "Right Eye HVF", right_template_path, extracted_data_objects, extracted_data_list)


                final_data_summary = "\n".join(extracted_data_list)
                if final_data_summary:
                    st.session_state.extracted_text = final_data_summary
                    st.session_state.extracted_data_objects = extracted_data_objects
                    st.success("Pipeline executed successfully!")
                else:
                    st.session_state.extracted_text = "Extraction failed or returned no data."
                    st.session_state.extracted_data_objects = []

        # Display the current state (helpful for debugging)
        st.write(f"Current extraction status: **{st.session_state.get('extracted_text', 'Text not extracted')}**")

        # --- Download Logic ---
        if st.session_state.extracted_data_objects:
            # Export format selection
            output_format = st.selectbox(
                "Select export format",
                ("CSV", "TXT", "JSON")
            )

            extracted_objects = st.session_state.get('extracted_data_objects', [])
            
            download_data, download_mime, download_filename = format_data_for_download(
                extracted_objects, 
                output_format
            )

            st.download_button(
                label=f"Download {output_format}",
                data=download_data,
                file_name=download_filename,
                mime=download_mime,
                icon=":material/download:",
            )

            with st.expander("Output"):
                st.write(
                    extracted_objects
                )
        
# Run the main function
if __name__ == '__main__':
    single_extraction_view()