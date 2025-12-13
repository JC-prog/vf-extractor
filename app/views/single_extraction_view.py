import streamlit as st
import os

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
  
# Run the main function
if __name__ == '__main__':
    single_extraction_view()