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

# ----------- DEFAULT USERS ----------
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
st.sidebar.title("🔐 Login")

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

# ---------------- CHANGE PASSWORD ----------------
st.sidebar.markdown("### 🔑 Change Password")

current = st.sidebar.text_input("Current Password", type="password")
new_pass = st.sidebar.text_input("New Password", type="password")

if st.sidebar.button("Update Password"):
    check = c.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (st.session_state["user"], current)
    ).fetchone()

    if check:
        c.execute(
            "UPDATE users SET password=? WHERE username=?",
            (new_pass, st.session_state["user"])
        )
        conn.commit()
        st.sidebar.success("Password Updated")
    else:
        st.sidebar.error("Wrong Current Password")

# ---------------- LOGOUT ----------------
if st.sidebar.button("Logout"):
    del st.session_state["user"]
    st.rerun()

# ---------------- HEADER ----------------
st.title("🏭 Production System")

report_date = st.date_input("📅 Date", date.today())
shift = st.selectbox("🌙 Shift", ["Day", "Night"])

machines = ["Machine 1", "Machine 2", "Machine 3"]

st.markdown("## 📊 Machine Totals")

cols = st.columns(3)

for i, m in enumerate(machines):
    total = c.execute(
        "SELECT SUM(qty) FROM production WHERE machine=? AND report_date=? AND shift=?",
        (m, str(report_date), shift)
    ).fetchone()[0]

    if total is None:
        total = 0

    cols[i].metric(m, total)

st.markdown("---")

# ---------------- QUICK ENTRY ----------------
st.markdown("## ➕ Quick Entry")

selected_machine = st.selectbox("Select Machine", machines)

qty = st.number_input("🔢 Quantity", min_value=0)

size = st.text_input("Size")
grade = st.selectbox("Grade", ["A", "B", "C"])

if st.button("Save Entry"):
    c.execute(
        "INSERT INTO production (machine, report_date, shift, size, grade, qty, entered_by) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (selected_machine, str(report_date), shift, size, grade, qty, st.session_state["user"])
    )
    conn.commit()
    st.success("Entry Saved Successfully!")
    st.rerun()

st.markdown("---")

# ---------------- REPORT ----------------
st.markdown("## 📋 Report")

df = pd.read_sql_query(
    "SELECT machine, qty, entered_by FROM production WHERE report_date=? AND shift=?",
    conn,
    params=(str(report_date), shift)
)

st.dataframe(df, use_container_width=True)

if st.button("Download Excel"):
    file_name = "production_report.xlsx"
    df.to_excel(file_name, index=False)
    st.success("Excel Ready!")
