# frontend/app.py

import streamlit as st
import os
import sys
from datetime import datetime
import importlib.util

# Get the absolute path of the project root directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Ensure the backend directory is in the Python path
backend_dir = os.path.join(project_root, 'backend')
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    from ingestion import extract_text
    from parser import extract_fields
    from database import insert_receipt, initialize_db
except ImportError as e:
    st.error(f"""
    Failed to import required modules. Please make sure you have:
    1. Installed all requirements: `pip install -r requirements.txt`
    2. Installed Tesseract OCR on your system
    3. Added Tesseract to your PATH
    
    Error: {str(e)}
    """)

st.set_page_config(page_title="Receipt Uploader", layout="centered")

st.title("Receipt Analyzer Upload Portal")

uploaded_file = st.file_uploader("Upload your receipt (.jpg, .png, .pdf, .txt)", type=["jpg", "png", "pdf", "txt"])

if uploaded_file is not None:
    # Save uploaded file temporarily
    file_path = os.path.join("temp_upload", uploaded_file.name)
    os.makedirs("temp_upload", exist_ok=True)
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getvalue())

    try:
        st.info("Extracting text from file...")
        raw_text = extract_text(file_path)
        st.success("Text extraction complete!")

        st.subheader(" OCR Text Output")
        st.text_area("Extracted Text", value=raw_text, height=200)

        receipt = extract_fields(raw_text)

        st.subheader("Parsed Receipt Fields")
        st.json({
            "Vendor": receipt.vendor,
            "Date": receipt.date.strftime('%Y-%m-%d'),
            "Amount": receipt.amount,
            "Category": receipt.category
        })

        initialize_db()
        insert_receipt(receipt)
        st.success(" Receipt saved to database!")

    except Exception as e:
        st.error(f"""
        Error processing receipt: {str(e)}
        
        If this is a Tesseract error, please make sure:
        1. Tesseract OCR is installed on your system
        2. The PATH environment variable includes Tesseract
        3. The image is clear and readable
        """)
    
    finally:
        # Clean up temporary file
        if os.path.exists(file_path):
            os.remove(file_path)
