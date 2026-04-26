import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

# ---------- DATABASE ----------
conn = sqlite3.connect("production.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS production (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_date TEXT,
    shift TEXT,
    machine TEXT,
    size TEXT,
    board TEXT,
    thickness TEXT,
    paper TEXT,
    finish TEXT,
    osr_qty INTEGER,
    a_qty INTEGER,
    b_qty INTEGER
)
""")
conn.commit()

# ---------- SESSION DEFAULTS ----------
if "size" not in st.session_state:
    st.session_state.size = ""
if "board" not in st.session_state:
    st.session_state.board = ""
if "thickness" not in st.session_state:
    st.session_state.thickness = ""

# ---------- UI ----------
st.title("📊 Production Entry App")

col1, col2, col3 = st.columns(3)
with col1:
    entry_date = st.date_input("Date", value=date.today())
with col2:
    shift = st.text_input("Shift")
with col3:
    machine = st.selectbox("Machine", ["M1","M2","M3","M4","M5","M6","M7"])

st.markdown("### 🔁 Static Fields (Auto Repeat)")
col4, col5, col6 = st.columns(3)
with col4:
    st.session_state.size = st.text_input("Size", value=st.session_state.size)
with col5:
    st.session_state.board = st.text_input("Board", value=st.session_state.board)
with col6:
    st.session_state.thickness = st.text_input("Thickness", value=st.session_state.thickness)

st.markdown("### ✍️ Daily Entry")

col7, col8, col9, col10, col11 = st.columns(5)
with col7:
    paper = st.text_input("Paper")
with col8:
    finish = st.text_input("Finish")
with col9:
    osr_qty = st.number_input("OSR Qty", min_value=0)
with col10:
    a_qty = st.number_input("A Qty", min_value=0)
with col11:
    b_qty = st.number_input("B Qty", min_value=0)

# ---------- SAVE ----------
if st.button("💾 Save Entry"):
    c.execute("""
    INSERT INTO production (
        entry_date, shift, machine, size, board, thickness,
        paper, finish, osr_qty, a_qty, b_qty
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        str(entry_date), shift, machine,
        st.session_state.size, st.session_state.board, st.session_state.thickness,
        paper, finish, osr_qty, a_qty, b_qty
    ))
    conn.commit()

    # CLEAR ONLY LAST ROW
    st.rerun()

# ---------- DISPLAY ----------
st.markdown("## 📋 Entries")

df = pd.read_sql("SELECT * FROM production WHERE entry_date = ?", conn, params=(str(entry_date),))
st.dataframe(df, use_container_width=True)

# ---------- TOTAL ----------
st.markdown("## 📊 Totals")

total_osr = df["osr_qty"].sum() if not df.empty else 0
total_a = df["a_qty"].sum() if not df.empty else 0
total_b = df["b_qty"].sum() if not df.empty else 0

st.success(f"OSR: {total_osr} | A: {total_a} | B: {total_b}")

# ---------- EXPORT ----------
if st.button("📥 Export Excel"):
    df.to_excel("report.xlsx", index=False)
    st.success("Excel Downloaded")
