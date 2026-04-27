import streamlit as st
import pandas as pd
from datetime import datetime
import io

st.set_page_config(page_title="Production App", layout="wide")

# ---------- CUSTOM CSS ----------
st.markdown("""
<style>
body {
    background-color: #f5f7fb;
}
h1 {
    text-align: center;
    color: #1f4e79;
}

/* Card style */
.block-container {
    padding: 1rem 1rem;
}

/* Buttons */
.stButton>button {
    width: 100%;
    border-radius: 10px;
    height: 45px;
    font-weight: bold;
}

/* Save button */
div.stButton:nth-child(1) button {
    background-color: #28a745;
    color: white;
}

/* Reset button */
div.stButton:nth-child(2) button {
    background-color: #dc3545;
    color: white;
}

/* Download button */
div.stDownloadButton button {
    background: linear-gradient(45deg, #6a11cb, #2575fc);
    color: white;
    height: 50px;
    border-radius: 12px;
    font-size: 16px;
}

/* Table */
table {
    border-radius: 10px;
    overflow: hidden;
}
</style>
""", unsafe_allow_html=True)

# ---------- TITLE ----------
st.title("📊 Daily Production Day and Night")

# ---------- SESSION STATE ----------
if "data" not in st.session_state:
    st.session_state.data = []

# ---------- FORM ----------
with st.container():

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        sno = len(st.session_state.data) + 1
        st.text_input("S.no", sno, disabled=True)

    with col2:
        shift = st.selectbox("Day/Night", ["Day", "Night"])

    with col3:
        machine = st.selectbox("Machine", ["Machine 1", "Machine 2", "Machine 3"])

    with col4:
        size = st.text_input("Size", "22x30")

    col5, col6, col7, col8 = st.columns(4)

    with col5:
        board = st.selectbox("Board type", ["Duplex Board", "Grey Board", "White Board"])

    with col6:
        thickness = st.selectbox("Thickness", ["200 GSM", "230 GSM", "250 GSM", "300 GSM", "350 GSM"])

    with col7:
        paper = st.selectbox("Paper", ["Kraft", "Ivory", "Art Paper"])

    with col8:
        finish = st.selectbox("Finish", ["Matte", "Gloss"])

    col9, col10, col11, col12 = st.columns(4)

    with col9:
        osr = st.text_input("OSR", "5%")

    with col10:
        a_grade = st.number_input("A Grade", 0)

    with col11:
        b_grade = st.number_input("B Grade", 0)

    with col12:
        qty = st.number_input("Qty", 0)

# ---------- BUTTONS ----------
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("💾 SAVE"):
        st.session_state.data.append({
            "S.no": sno,
            "Shift": shift,
            "Machine": machine,
            "Size": size,
            "Board": board,
            "Thickness": thickness,
            "Paper": paper,
            "Finish": finish,
            "OSR": osr,
            "A Grade": a_grade,
            "B Grade": b_grade,
            "Qty": qty
        })
        st.success("Saved!")

with col_btn2:
    if st.button("🗑 RESET"):
        st.session_state.data = []
        st.warning("All data cleared!")

# ---------- TABLE ----------
st.subheader("📋 Saved Entries")

if st.session_state.data:
    df = pd.DataFrame(st.session_state.data)
    st.dataframe(df, use_container_width=True)

    # ---------- DOWNLOAD ----------
    excel_buffer = io.BytesIO()
    df.to_excel(excel_buffer, index=False)
    excel_buffer.seek(0)

    st.download_button(
        "⬇ Download Excel",
        data=excel_buffer,
        file_name="production.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.info("No data yet")

# ---------- FOOTER ----------
st.markdown("""
---
✅ You can edit or delete entries soon  
📥 Use download button to export data
""")
