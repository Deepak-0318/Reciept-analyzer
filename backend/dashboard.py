# dashboard.py

import streamlit as st
import pandas as pd
from database import create_connection
from datetime import datetime

st.set_page_config(page_title="Receipt Analyzer Dashboard", layout="wide")

# --------------------
# Load data from DB
# --------------------
def load_receipts():
    conn = create_connection()
    query = "SELECT vendor, date, amount, category FROM receipts"
    df = pd.read_sql_query(query, conn, parse_dates=['date'])
    conn.close()
    return df

# --------------------
# Dashboard UI
# --------------------
st.title("🧾 Receipt Analyzer Dashboard")

df = load_receipts()

# Show raw data table
st.subheader("📋 All Receipts")
st.dataframe(df.sort_values(by="date", ascending=False), use_container_width=True)

# Filter by vendor
vendors = df['vendor'].unique().tolist()
selected_vendor = st.sidebar.selectbox("🔍 Filter by Vendor", ["All"] + vendors)
if selected_vendor != "All":
    df = df[df['vendor'] == selected_vendor]

# Filter by date range
min_date, max_date = df["date"].min(), df["date"].max()
date_range = st.sidebar.date_input("📅 Filter by Date Range", [min_date, max_date])
if len(date_range) == 2:
    start_date, end_date = date_range
    df = df[(df["date"] >= pd.to_datetime(start_date)) & (df["date"] <= pd.to_datetime(end_date))]

# Show filtered results
st.subheader("📄 Filtered Receipts")
st.write(f"Showing {len(df)} receipts")
st.dataframe(df.sort_values(by="date", ascending=False), use_container_width=True)

# --------------------
# Analytics
# --------------------
st.subheader("📊 Analytics")

col1, col2 = st.columns(2)

# Total Spend by Category
with col1:
    st.markdown("#### 💸 Total Spend by Category")
    category_chart = df.groupby("category")["amount"].sum().sort_values(ascending=False)
    st.bar_chart(category_chart)

# Total Spend by Month
with col2:
    st.markdown("#### 📈 Monthly Spend")
    df["month"] = df["date"].dt.to_period("M").astype(str)
    month_chart = df.groupby("month")["amount"].sum().sort_index()
    st.line_chart(month_chart)

# --------------------
# Download Option
# --------------------
st.subheader("⬇️ Export Filtered Data")
csv_data = df.to_csv(index=False).encode('utf-8')
st.download_button("Download CSV", data=csv_data, file_name="receipts.csv", mime='text/csv')
