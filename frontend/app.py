# frontend/app.py

import streamlit as st
import os
import sys
from datetime import datetime

# Add backend path to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from ingestion import extract_text
from parser import extract_fields
from database import insert_receipt, initialize_db

st.set_page_config(page_title="Receipt Uploader", layout="centered")

st.title("📤 Receipt Analyzer Upload Portal")

uploaded_file = st.file_uploader("Upload your receipt (.jpg, .png, .pdf, .txt)", type=["jpg", "png", "pdf", "txt"])

if uploaded_file is not None:
    # Save uploaded file temporarily
    file_path = os.path.join("temp_upload", uploaded_file.name)
    os.makedirs("temp_upload", exist_ok=True)
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getvalue())

    try:
        st.info("🔍 Extracting text from file...")
        raw_text = extract_text(file_path)
        st.success("✅ Text extraction complete!")

        st.subheader("📝 OCR Text Output")
        st.text_area("Extracted Text", value=raw_text, height=200)

        receipt = extract_fields(raw_text)

        st.subheader("🧾 Parsed Receipt Fields")
        st.json({
            "Vendor": receipt.vendor,
            "Date": receipt.date.strftime('%Y-%m-%d'),
            "Amount": receipt.amount,
            "Category": receipt.category
        })

        initialize_db()
        insert_receipt(receipt)
        st.success("✅ Receipt saved to database!")

    except Exception as e:
        st.error(f"❌ Error: {e}")

    finally:
        os.remove(file_path)
