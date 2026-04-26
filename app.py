import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
import os

# PAGE CONFIG
st.set_page_config(
    page_title="Production System",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# DATABASE CONNECTION - FIX FOR LOCKING ISSUES
@st.cache_resource
def get_connection():
    conn = sqlite3.connect("production.db", check_same_thread=False, timeout=30)
    conn.isolation_level = None  # Autocommit mode
    return conn

conn = get_connection()
c = conn.cursor()

# CREATE TABLES WITH CORRECT SCHEMA
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
    size TEXT,
    board TEXT,
    thickness TEXT,
    paper TEXT,
    finish TEXT,
    osr TEXT,
    qty_a INTEGER,
    qty_b INTEGER,
    report_date TEXT,
    shift TEXT,
    entered_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# DEFAULT USERS
default_users = {
    "user1": "124",
    "user2": "123",
    "user3": "123",
    "user4": "123",
    "user5": "123"
}

for u, p in default_users.items():
    c.execute("INSERT OR IGNORE INTO users VALUES (?,?)", (u, p))

# LOGIN SCREEN
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

# HEADER
st.markdown(f"### 👋 Welcome, {st.session_state['user']}")

if st.button("🚪 Logout", use_container_width=True):
    del st.session_state["user"]
    st.rerun()

st.divider()

# FILTERS
col1, col2 = st.columns(2)

with col1:
    report_date = st.date_input("📅 Date", date.today())

with col2:
    shift = st.selectbox("🌙 Shift", ["Day", "Night"])

machines = ["Machine 1", "Machine 2", "Machine 3", "Machine 4", "Machine 5", "Machine 6", "Machine 7"]

st.divider()

# DASHBOARD - SAFE DATABASE QUERY
st.subheader("📊 Production Dashboard")

total_a = 0
total_b = 0
cols = st.columns(len(machines))

report_date_str = str(report_date)  # Convert to string for consistent querying

for i, m in enumerate(machines):
    try:
        result = c.execute(
            "SELECT SUM(qty_a), SUM(qty_b) FROM production WHERE machine=? AND report_date=? AND shift=?",
            (m, report_date_str, shift)
        ).fetchone()

        qty_a = result[0] if result[0] else 0
        qty_b = result[1] if result[1] else 0
        total = qty_a + qty_b
        total_a += qty_a
        total_b += qty_b

        cols[i].metric(m, total)
    except Exception as e:
        cols[i].error("Error")

col_total1, col_total2, col_total3 = st.columns(3)
col_total1.metric("🏭 Total A", int(total_a))
col_total2.metric("🏭 Total B", int(total_b))
col_total3.metric("🏭 Total (A+B)", int(total_a + total_b))

st.divider()

# FORM STATE
if "selected_machine" not in st.session_state:
    st.session_state.selected_machine = machines[0]

# ENTRY FORM
with st.expander("➕ Add Production Entry", expanded=True):

    # MOBILE RESPONSIVE - Single Column on Mobile
    st.subheader("Machine & Size")
    form_col1, form_col2 = st.columns([1, 1])
    
    with form_col1:
        selected_machine = st.selectbox(
            "🤖 Machine", machines,
            key="machine_select"
        )
    
    with form_col2:
        size_input = st.text_input("📏 Size", placeholder="e.g., Size 1", key="size_input")

    st.markdown("---")
    
    # Board, Thickness, Paper - 3 columns or responsive
    st.subheader("Materials & Specifications")
    col_board, col_thick, col_paper = st.columns(3)
    
    with col_board:
        board_input = st.text_input("📦 Board", placeholder="e.g., Board A", key="board_input")
    
    with col_thick:
        thickness_input = st.text_input("📐 Thickness", placeholder="e.g., 2mm", key="thickness_input")
    
    with col_paper:
        paper_input = st.text_input("📄 Paper", placeholder="e.g., Paper A", key="paper_input")

    st.markdown("---")
    
    # Finish & OSR
    st.subheader("Finish & Settings")
    col_finish, col_osr = st.columns(2)
    
    with col_finish:
        finish_input = st.text_input("✨ Finish", placeholder="e.g., Gloss", key="finish_input")
    
    with col_osr:
        osr_input = st.text_input("🔧 OSR", placeholder="e.g., OSR 1", key="osr_input")

    st.markdown("---")
    
    # QUANTITIES - IMPORTANT SECTION
    st.subheader("📊 Production Quantities")
    qty_col1, qty_col2 = st.columns(2)
    
    with qty_col1:
        qty_a = st.number_input("📊 Quantity A", min_value=0, key="qty_a_input", value=0, step=1)
    
    with qty_col2:
        qty_b = st.number_input("📊 Quantity B", min_value=0, key="qty_b_input", value=0, step=1)

    st.markdown("---")
    
    if st.button("💾 Save Entry", use_container_width=True):
        # VALIDATION
        if not selected_machine:
            st.error("❌ Please select a Machine")
        elif not size_input.strip():
            st.error("❌ Please enter Size")
        elif not board_input.strip():
            st.error("❌ Please enter Board")
        elif not thickness_input.strip():
            st.error("❌ Please enter Thickness")
        elif not paper_input.strip():
            st.error("❌ Please enter Paper")
        elif not finish_input.strip():
            st.error("❌ Please enter Finish")
        elif not osr_input.strip():
            st.error("❌ Please enter OSR")
        elif qty_a == 0 and qty_b == 0:
            st.error("❌ Please enter Quantity A or B")
        else:
            try:
                c.execute(
                    """INSERT INTO production 
                    (machine, size, board, thickness, paper, finish, osr, qty_a, qty_b, report_date, shift, entered_by) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (selected_machine, size_input.strip(), board_input.strip(), 
                     thickness_input.strip(), paper_input.strip(), finish_input.strip(), osr_input.strip(), 
                     int(qty_a), int(qty_b), report_date_str, shift, st.session_state["user"])
                )
                st.success("✅ Entry saved successfully!")
                # Clear inputs
                st.session_state.size_input = ""
                st.session_state.board_input = ""
                st.session_state.thickness_input = ""
                st.session_state.paper_input = ""
                st.session_state.finish_input = ""
                st.session_state.osr_input = ""
                st.session_state.qty_a_input = 0
                st.session_state.qty_b_input = 0
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error saving entry: {str(e)}")

st.divider()

# REPORT
st.subheader("📋 Production Report")

filter_machine = st.selectbox("🔍 Filter Machine", ["All"] + machines)

query = "SELECT id, machine, size, board, thickness, paper, finish, osr, qty_a, qty_b, report_date, shift, entered_by FROM production WHERE report_date=? AND shift=?"
params = [report_date_str, shift]

if filter_machine != "All":
    query += " AND machine=?"
    params.append(filter_machine)

query += " ORDER BY id DESC"

try:
    df = pd.read_sql_query(query, conn, params=params)

    if not df.empty:
        df = df.rename(columns={
            'id': 'ID', 'machine': 'Machine', 'size': 'Size',
            'board': 'Board', 'thickness': 'Thickness', 'paper': 'Paper',
            'finish': 'Finish', 'osr': 'OSR', 'qty_a': 'Qty A', 'qty_b': 'Qty B',
            'report_date': 'Date', 'shift': 'Shift', 'entered_by': 'Entered By'
        })
        
        st.dataframe(df, use_container_width=True, hide_index=True)

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "⬇️ Download CSV", csv,
            f"production_report_{report_date}.csv", "text/csv",
            use_container_width=True
        )
    else:
        st.info("📊 No data found for selected date and shift")
except Exception as e:
    st.error(f"❌ Error loading report: {str(e)}")

st.divider()

# STYLING - MOBILE RESPONSIVE
st.markdown("""
<style>
    /* Button Styling */
    .stButton button {
        height: 50px;
        font-size: 16px;
        border-radius: 10px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        transform: scale(1.02);
    }
    
    /* Input Fields */
    .stTextInput input, 
    .stNumberInput input, 
    .stSelectbox select {
        height: 45px;
        border-radius: 8px;
    }
    
    /* Metrics */
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
    
    /* Divider */
    hr {
        margin: 20px 0;
    }
    
    /* Mobile Responsive */
    @media (max-width: 768px) {
        .stButton button {
            height: 45px;
            font-size: 14px;
        }
        
        .stTextInput input, 
        .stNumberInput input, 
        .stSelectbox select {
            height: 40px;
            font-size: 14px;
        }
        
        .stMetric {
            padding: 10px;
        }
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #e8f0f7;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)
