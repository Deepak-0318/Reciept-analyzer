# parser.py

import re
import os
import sys
from datetime import datetime

# --- Module-safe imports ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.models import Receipt
from backend.database import insert_receipt, initialize_db
from ingestion import extract_text  # No relative import; absolute works from backend/

# --- Known vendor mappings ---
KNOWN_VENDORS = {
    "Reliance": "Groceries",
    "Amazon": "Shopping",
    "Bescom": "Electricity",
    "Airtel": "Internet"
}

def parse_vendor(text):
    text_lower = text.lower()
    for vendor, category in KNOWN_VENDORS.items():
        if vendor.lower() in text_lower:
            return vendor, category

    lines = text.strip().splitlines()
    first_line = lines[0] if lines else "Unknown Vendor"
    return first_line.strip(), "Other"

def parse_date(text):
    lines = text.splitlines()

    # 1. Line-by-line: Check for Receipt Date
    for line in lines:
        if "date" in line.lower():
            match = re.search(r"(\d{2}[/-]\d{2}[/-]\d{2,4}|\d{8})", line)
            if match:
                date_str = match.group(1)
                formats = ['%d/%m/%Y', '%d-%m-%Y', '%d/%m/%y', '%d-%m-%y', '%d%m%Y']
                for fmt in formats:
                    try:
                        return datetime.strptime(date_str, fmt)
                    except ValueError:
                        continue

    # 2. Generic full-text scan for patterns
    patterns = [
        r"\b\d{2}[/-]\d{2}[/-]\d{4}\b",   # 29/07/2025
        r"\b\d{4}[/-]\d{2}[/-]\d{2}\b",   # 2025-07-29
        r"\b\d{2}[/-]\d{2}[/-]\d{2}\b",   # 29/07/25
        r"\b\d{8}\b",                     # 29072025
        r"\b\d{1,2} (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}\b",
        r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b"
    ]
    formats = [
        '%d-%m-%Y', '%d/%m/%Y', '%Y-%m-%d', '%Y/%m/%d',
        '%d-%m-%y', '%d/%m/%y', '%d%m%Y',
        '%d %B %Y', '%B %d, %Y', '%d %b %Y', '%b %d, %Y'
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            date_str = match.group()
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue

    print("⚠️ Warning: No date found in receipt. Using current date instead.")
    return datetime.today()

def parse_amount(text):
    # Priority: Lines containing 'TOTAL'
    total_match = re.search(r'TOTAL\s*[:\-]?\s*₹?\s*(\d+(?:,\d+)*\.?\d*)', text, re.IGNORECASE)
    if total_match:
        amount_str = total_match.group(1).replace(',', '')
        return float(amount_str)

    # Fallback to any amount-looking number
    match = re.findall(r'(?:Total|Amount|Rs|INR)?\s*[:\-]?\s*₹?\s*(\d+(?:,\d+)*\.?\d*)', text, re.IGNORECASE)
    if match:
        amount_str = match[-1].replace(',', '')
        return float(amount_str)

    raise ValueError("Amount not found")

def extract_fields(raw_text):
    vendor, category = parse_vendor(raw_text)

    try:
        date = parse_date(raw_text)
    except Exception as e:
        print("⚠️ Could not parse date, using current date. Reason:", e)
        date = datetime.today()

    amount = parse_amount(raw_text)

    receipt_data = {
        "vendor": vendor,
        "date": date,
        "amount": amount,
        "category": category
    }

    return Receipt(**receipt_data)

# --- Manual test ---
if __name__ == "__main__":
    # Use receipt image from ../data/
    file_path = os.path.join(project_root, "data", "2sample.png")

    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        sys.exit(1)

    try:
        print(f"Processing receipt: {file_path}")
        raw_text = extract_text(file_path)

        print("\nExtracted text from receipt:")
        print("-" * 40)
        print(raw_text)
        print("-" * 40 + "\n")

        receipt = extract_fields(raw_text)
        print("Parsed Receipt:")
        print(receipt.model_dump_json(indent=2))

        # Insert into DB
        initialize_db()
        insert_receipt(receipt)
        print("✅ Receipt inserted into the database")

    except Exception as e:
        print("❌ Error:", e)
