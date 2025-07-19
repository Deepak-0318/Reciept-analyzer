# database.py

import sqlite3
from pathlib import Path
try:
    from backend.models import Receipt
except ImportError:
    from models import Receipt

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "receipts.db"

def create_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

def initialize_db():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS receipts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendor TEXT NOT NULL,
            date TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT
        )
    ''')
    # Indexing for fast search
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_vendor ON receipts(vendor)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_date ON receipts(date)')
    conn.commit()
    conn.close()

def insert_receipt(receipt: Receipt):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO receipts (vendor, date, amount, category)
        VALUES (?, ?, ?, ?)
    ''', (receipt.vendor, receipt.date.isoformat(), receipt.amount, receipt.category))
    conn.commit()
    conn.close()
