import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date

# ---------- GOOGLE SHEETS ----------
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)

sheet = client.open("ProductionData").sheet1

# ---------- SESSION ----------
if "size" not in st.session_state:
    st.session_state.size = ""
if "board" not in st.session_state:
    st.session_state.board = ""
if "thickness" not in st.session_state:
    st.session_state.thickness = ""

# ---------- UI ----------
st.title("📱 Production Entry (Online)")

col1, col2, col3 = st.columns(3)
with col1:
    entry_date = st.date_input("Date", value=date.today())
with col2:
    shift = st.text_input("Shift")
with col3:
    machine = st.selectbox("Machine", ["M1","M2","M3","M4","M5","M6","M7"])

st.markdown("### 🔁 Static Fields")
col4, col5, col6 = st.columns(3)
with col4:
    st.session_state.size = st.text_input("Size", value=st.session_state.size)
with col5:
    st.session_state.board = st.text_input("Board", value=st.session_state.board)
with col6:
    st.session_state.thickness = st.text_input("Thickness", value=st.session_state.thickness)

st.markdown("### ✍️ Entry")

col7, col8, col9, col10, col11 = st.columns(5)
with col7:
    paper = st.text_input("Paper")
with col8:
    finish = st.text_input("Finish")
with col9:
    osr = st.number_input("OSR", min_value=0)
with col10:
    a = st.number_input("A Qty", min_value=0)
with col11:
    b = st.number_input("B Qty", min_value=0)

# ---------- SAVE ----------
if st.button("💾 Save"):
    sheet.append_row([
        str(entry_date), shift, machine,
        st.session_state.size,
        st.session_state.board,
        st.session_state.thickness,
        paper, finish, osr, a, b
    ])
    st.success("Saved!")
    st.rerun()

# ---------- LOAD DATA ----------
data = sheet.get_all_records()
df = pd.DataFrame(data)

if not df.empty:
    df_today = df[df["Date"] == str(entry_date)]

    st.markdown("## 📋 Data")
    st.dataframe(df_today, use_container_width=True)

    # ---------- TOTAL ----------
    st.markdown("## 📊 Totals")
    st.success(f"""
    OSR: {df_today['OSR'].sum()}  
    A: {df_today['A'].sum()}  
    B: {df_today['B'].sum()}
    """)

    # ---------- EXPORT ----------
    st.download_button("📥 Download Excel", df_today.to_csv(index=False), "report.csv")
