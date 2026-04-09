import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Production System",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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

# ---------------- DEFAULT USERS ----------------
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

# ---------------- LOGIN SCREEN ----------------
if "user" not in st.session_state:

    st.markdown("## 🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login", use_container_width=True):
        user = c.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        ).fetchone()

        if user:
            st.session_state["user"] = username
            st.rerun()
        else:
            st.error("Wrong Username/Password")

    st.stop()

# ---------------- HEADER ----------------
st.markdown(f"### 👋 Welcome, {st.session_state['user']}")

if st.button("🚪 Logout", use_container_width=True):
    del st.session_state["user"]
    st.rerun()

st.divider()

# ---------------- TOP FILTERS ----------------
col1, col2 = st.columns(2)

with col1:
    report_date = st.date_input("📅 Date", date.today())

with col2:
    shift = st.selectbox("🌙 Shift", ["Day", "Night"])

machines = ["Machine 1", "Machine 2", "Machine 3", "Machine 4", "Machine 5", "Machine 6", "Machine 7" ]

st.divider()

# ---------------- DASHBOARD ----------------
st.subheader("📊 Production Dashboard")

total_all = 0

cols = st.columns(len(machines))

for i, m in enumerate(machines):
    total = c.execute(
        "SELECT SUM(qty) FROM production WHERE machine=? AND report_date=? AND shift=?",
        (m, str(report_date), shift)
    ).fetchone()[0]

    total = total or 0
    total_all += total

    cols[i].metric(m, total)

st.metric("🏭 Total Production", total_all)

st.divider()

# ---------------- ENTRY FORM ----------------
with st.expander("➕ Add Production Entry", expanded=True):

    selected_machine = st.selectbox("Machine", machines)
    size = st.text_input("Size")
    grade = st.selectbox("Grade", ["A", "B", "C"])
    qty = st.number_input("Quantity", min_value=0)

    if st.button("Save Entry", use_container_width=True):
        c.execute(
            "INSERT INTO production (machine, report_date, shift, size, grade, qty, entered_by) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (selected_machine, str(report_date), shift, size, grade, qty, st.session_state["user"])
        )
        conn.commit()
        st.success("✅ Saved Successfully!")
        st.rerun()

st.divider()

# ---------------- REPORT SECTION ----------------
st.subheader("📋 Production Report")

filter_machine = st.selectbox("Filter Machine", ["All"] + machines)

query = "SELECT * FROM production WHERE report_date=? AND shift=?"
params = [str(report_date), shift]

if filter_machine != "All":
    query += " AND machine=?"
    params.append(filter_machine)

df = pd.read_sql_query(query, conn, params=params)

if not df.empty:

    st.dataframe(df, use_container_width=True)

    # DOWNLOAD CSV
    csv = df.to_csv(index=False).encode('utf-8')

    st.download_button(
        "⬇ Download CSV",
        csv,
        "production_report.csv",
        "text/csv",
        use_container_width=True
    )

else:
    st.info("No data found")

st.divider()

# ---------------- SIMPLE STYLING ----------------
st.markdown("""
<style>
    .stButton button {
        height: 50px;
        font-size: 16px;
        border-radius: 10px;
    }
    .stTextInput input, .stNumberInput input {
        height: 45px;
    }
</style>
""", unsafe_allow_html=True)
