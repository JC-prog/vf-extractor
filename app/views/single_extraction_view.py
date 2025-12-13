import streamlit as st
import os
import sys
import tempfile
from io import BytesIO

# Import custom package
current_dir = os.path.dirname(__file__)
root_dir = os.path.join(current_dir, '..', '..')

if root_dir not in sys.path:
    sys.path.append(root_dir)

try:
    import vfextractor
    from vfextractor.postprocessing.extract import Extractor
except ModuleNotFoundError as e:
    st.error(f"Error loading module: {e}. Check directory structure.")

def single_extraction_view():
    st.title("Single File Extractor")

    le_col, re_col = st.columns(2)

    # Left Eye Container
    with le_col:
        st.header("Left Eye - OS")

        le_hvf_container = st.container()
        with le_hvf_container:
            uploaded_file_lehvf = st.file_uploader(
                "Upload **HVF** image file (PNG/JPG)",
                type=["png", "jpg", "jpeg"],
                key="lehvf_uploader"
            )
            
            # Display logic for Left Eye HVF
            if uploaded_file_lehvf is not None:
                st.success(f"File uploaded: {uploaded_file_lehvf.name}")
                st.image(
                    uploaded_file_lehvf, 
                    caption=f"Preview: {uploaded_file_lehvf.name}"
                )

    # Right Eye Container            
    with re_col:
        st.header("Right Eye - OD")

        re_hvf_container = st.container()
        with re_hvf_container:
            uploaded_file_rehvf = st.file_uploader(
                "Upload **HVF** image file (PNG/JPG)",
                type=["png", "jpg", "jpeg"],
                key="rehvf_uploader"
            )
            
            # Display logic for Right Eye HVF
            if uploaded_file_rehvf is not None:
                st.success(f"File uploaded: {uploaded_file_rehvf.name}")
                st.image(
                    uploaded_file_rehvf, 
                    caption=f"Preview: {uploaded_file_rehvf.name}"
                )
    
    # Buttons
    function_container = st.container()
    
    with function_container:
        if 'extracted_text' not in st.session_state:
            st.session_state.extracted_text = "Text not extracted"

        pipeline_button = st.button("Run Pipeline", type="primary")

        if pipeline_button:

            if uploaded_file_lehvf is None and uploaded_file_rehvf is None:
                st.warning("Please upload at least one image file (HVF) for extraction.")

                st.session_state.extracted_text = "No file uploaded."
            else:
                with st.spinner("Processing files and extracting data... This may take a moment."):
                    vf_extractor = Extractor()
                    
                    extracted_data_list = []
                    
                    # Process Left Eye HVF
                    if uploaded_file_lehvf is not None:
                        # Use tempfile.NamedTemporaryFile for automatic cleanup
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
                            # Go to the start of the file object
                            uploaded_file_lehvf.seek(0) 
                            # Write the contents of the UploadedFile to the temporary file
                            tmp_file.write(uploaded_file_lehvf.read())
                            tmp_file_path = tmp_file.name
                        
                        try:
                            # Pass the file path (str) to the extractor
                            data_lehvf = vf_extractor.extract(tmp_file_path)
                            extracted_data_list.append(f"Left Eye HVF Data: {data_lehvf}")
                        except Exception as e:
                            st.error(f"Extraction failed for Left Eye HVF: {e}")
                        finally:
                            # Ensure the temporary file is deleted after use
                            os.unlink(tmp_file_path)

                    # Process Right Eye HVF (Add logic for rehvf if needed)
                    # ... (You would duplicate the above 'if uploaded_file_lehvf is not None' logic here for uploaded_file_rehvf) ...

                    # 4. Update session state and display success
                    final_data = "\n".join(extracted_data_list)
                    if final_data:
                        st.session_state.extracted_text = final_data
                        st.success("Pipeline executed successfully!")
                    else:
                        st.session_state.extracted_text = "Extraction failed or returned no data."

        # The data for download is taken directly from the session state
        csv_data = st.session_state.extracted_text 

        # Display the current state (helpful for debugging)
        st.write(f"Current extraction status: **{csv_data}**")

        st.download_button(
            label="Download TXT",
            data=csv_data,
            file_name="data.txt",
            mime="text/plain",
            icon=":material/download:",
        )
        
  
# Run the main function
if __name__ == '__main__':
    single_extraction_view()