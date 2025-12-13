import streamlit as st
import os
import sys

# View Imports
from views.single_extraction_view import single_extraction_view
from views.batch_extraction_view import batch_extraction_view

# TODO: App checker
APP_READY = True

def main():
    st.set_page_config(page_title="HVF Report Data Extractor", layout="wide")
    
    # --- Sidebar Navigation ---
    with st.sidebar:
        st.header("Views")
        
        # 1. Navigation Selector
        view_selection = st.radio(
            "Select View",
            options=["Single Extract", "Batch Extract"],
            index=0,
        )
        

    # --- View Content Switching ---
    if view_selection == "Single Extract":
        single_extraction_view() 

    elif view_selection == "Batch Extract":
        batch_extraction_view() 


if __name__ == "__main__":
    if os.getcwd() not in sys.path:
        sys.path.append(os.getcwd())
        
    if APP_READY:
        main()