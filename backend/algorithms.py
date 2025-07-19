# algorithms.py

import sqlite3
from datetime import datetime
from collections import defaultdict
from pathlib import Path
try:
    from backend.models import Receipt
except ImportError:
    from models import Receipt
# Define DB path
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "receipts.db"

# Create a DB connection
def create_connection():
    return sqlite3.connect(DB_PATH)

# Utility to convert DB row to Receipt model
def row_to_receipt(row):
    return Receipt(
        vendor=row[0],
        date=datetime.fromisoformat(row[1]),
        amount=row[2],
        category=row[3]
    )

# 1. Search receipts by vendor keyword
def search_receipts(keyword):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT vendor, date, amount, category FROM receipts 
        WHERE LOWER(vendor) LIKE ?
    """, (f"%{keyword.lower()}%",))
    rows = cursor.fetchall()
    conn.close()
    return [row_to_receipt(row) for row in rows]

# 2. Filter receipts between two dates (inclusive)
def filter_receipts_by_date(start_date: datetime, end_date: datetime):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT vendor, date, amount, category FROM receipts 
        WHERE date BETWEEN ? AND ?
    """, (start_date.isoformat(), end_date.isoformat()))
    rows = cursor.fetchall()
    conn.close()
    return [row_to_receipt(row) for row in rows]

# 3. Sort receipts by date or amount
def sort_receipts(by="date", order="asc"):
    if by not in ["date", "amount"] or order not in ["asc", "desc"]:
        raise ValueError("Invalid sorting parameters")
    
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT vendor, date, amount, category FROM receipts 
        ORDER BY {by} {order.upper()}
    """)
    rows = cursor.fetchall()
    conn.close()
    return [row_to_receipt(row) for row in rows]

# 4. Aggregate total spend by category
def aggregate_by_category():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT category, SUM(amount) FROM receipts GROUP BY category
    """)
    results = cursor.fetchall()
    conn.close()
    return {category if category else "Uncategorized": total for category, total in results}

# 5. Aggregate spend by year-month
def aggregate_by_month():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT strftime('%Y-%m', date) as month, SUM(amount) 
        FROM receipts GROUP BY month ORDER BY month
    """)
    results = cursor.fetchall()
    conn.close()
    return {month: total for month, total in results}

# --- Optional: test run ---
if __name__ == "__main__":
    print("🔍 Search for vendor 'amazon':")
    for r in search_receipts("amazon"):
        print(r)

    print("\n📅 Filter by date:")
    for r in filter_receipts_by_date(datetime(2023, 1, 1), datetime(2025, 12, 31)):
        print(r)

    print("\n⬆️ Sorted by amount descending:")
    for r in sort_receipts(by="amount", order="desc"):
        print(r)

    print("\n📊 Total spend by category:")
    print(aggregate_by_category())

    print("\n📈 Total spend by month:")
    print(aggregate_by_month())
