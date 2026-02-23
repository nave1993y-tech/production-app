import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

# ---------------- DATABASE ----------------
conn = sqlite3.connect("production.db", check_same_thread=False)
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS production (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    machine TEXT,
    report_date TEXT,
    shift TEXT,
    size TEXT,
    grade TEXT,
    qty INTEGER,
    entered_by TEXT
)
''')

conn.commit()

# ----------- DEFAULT USERS (5 LOG) ----------
default_users = {
    "user1": "123",
    "user2": "123",
    "user3": "123",
    "user4": "123",
    "user5": "123"
}

for u, p in default_users.items():
    c.execute("INSERT OR IGNORE INTO users VALUES (?,?)", (u, p))
conn.commit()

# ---------------- LOGIN ----------------
st.sidebar.title("Login")

username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Login"):
    user = c.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, password)
    ).fetchone()

    if user:
        st.session_state["user"] = username
    else:
        st.sidebar.error("Wrong Login")

if "user" not in st.session_state:
    st.stop()

st.sidebar.success(f"Logged in as {st.session_state['user']}")

# ---------------- HEADER ----------------
st.title("🏭 Production System")

report_date = st.date_input("Date", date.today())
shift = st.selectbox("Shift", ["Day", "Night"])

machines = ["Machine 1", "Machine 2", "Machine 3"]

st.divider()

# ---------------- MACHINE TOTALS ----------------
st.subheader("Machine Totals")

for m in machines:
    total = c.execute(
        "SELECT SUM(qty) FROM production WHERE machine=? AND report_date=? AND shift=?",
        (m, str(report_date), shift)
    ).fetchone()[0]

    if total is None:
        total = 0

    st.write(f"{m} → {total}")

st.divider()

# ---------------- QUICK ENTRY ----------------
st.subheader("Quick Entry")

selected_machine = st.selectbox("Machine", machines)

col1, col2 = st.columns(2)

with col1:
    size = st.text_input("Size")
    grade = st.selectbox("Grade", ["A", "B", "C"])

with col2:
    qty = st.number_input("Quantity", min_value=0)

if st.button("Save Entry"):
    c.execute(
        "INSERT INTO production (machine, report_date, shift, size, grade, qty, entered_by) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (selected_machine, str(report_date), shift, size, grade, qty, st.session_state["user"])
    )
    conn.commit()
    st.success("Saved Successfully!")

st.divider()

# ---------------- REPORT ----------------
st.subheader("Report")

df = pd.read_sql_query(
    "SELECT * FROM production WHERE report_date=? AND shift=?",
    conn,
    params=(str(report_date), shift)
)

st.dataframe(df)

if st.button("Download Excel"):
    file_name = "production_report.xlsx"
    df.to_excel(file_name, index=False)
    st.success("Excel Ready!")
