import streamlit as st
import pandas as pd
from io import BytesIO
from fpdf import FPDF
import os

st.set_page_config(page_title="Production App", layout="wide")

FILE = "data.xlsx"

# Load data
if os.path.exists(FILE):
    df = pd.read_excel(FILE)
else:
    df = pd.DataFrame(columns=[
        "Day/Night","Machine","Size","Board type",
        "Thickness","Paper","Finish","OSR",
        "A Grade","B Grade","Qty"
    ])

st.markdown("## 📊 Daily Production - Day & Night")

# ---------- FORM ----------
with st.container():
    st.markdown("### ➕ New Entry")

    col1, col2 = st.columns(2)

    day = col1.selectbox("Day/Night", ["Day", "Night"])
    machine = col2.text_input("Machine")

    size = col1.text_input("Size")
    board = col2.text_input("Board Type")

    thickness = col1.text_input("Thickness")
    paper = col2.text_input("Paper")

    finish = col1.text_input("Finish")
    osr = col2.number_input("OSR", 0)

    a = col1.number_input("A Grade", 0)
    b = col2.number_input("B Grade", 0)

    qty = st.number_input("Qty", 0)

    if st.button("💾 Save Entry"):
        new_row = pd.DataFrame([[day,machine,size,board,thickness,paper,finish,osr,a,b,qty]],
        columns=df.columns)

        df = pd.concat([df,new_row], ignore_index=True)
        df.to_excel(FILE, index=False)
        st.success("✅ Entry Saved")

# ---------- DATA TABLE ----------
st.markdown("### 📋 Data")

st.dataframe(df, use_container_width=True, height=300)

# ---------- EDIT ----------
st.markdown("### ✏ Edit Row")

edit_index = st.number_input("Enter Row Number to Edit", min_value=1, step=1)

if st.button("Load Row"):
    if edit_index <= len(df):
        row = df.iloc[edit_index-1]
        st.session_state["edit_data"] = row

if "edit_data" in st.session_state:
    row = st.session_state["edit_data"]

    col1, col2 = st.columns(2)

    day_e = col1.selectbox("Day/Night", ["Day","Night"], index=0 if row[0]=="Day" else 1)
    machine_e = col2.text_input("Machine", row[1])

    size_e = col1.text_input("Size", row[2])
    board_e = col2.text_input("Board Type", row[3])

    thickness_e = col1.text_input("Thickness", row[4])
    paper_e = col2.text_input("Paper", row[5])

    finish_e = col1.text_input("Finish", row[6])
    osr_e = col2.number_input("OSR", value=int(row[7]))

    a_e = col1.number_input("A Grade", value=int(row[8]))
    b_e = col2.number_input("B Grade", value=int(row[9]))

    qty_e = st.number_input("Qty", value=int(row[10]))

    if st.button("Update Row"):
        df.iloc[edit_index-1] = [day_e,machine_e,size_e,board_e,thickness_e,paper_e,finish_e,osr_e,a_e,b_e,qty_e]
        df.to_excel(FILE, index=False)
        st.success("✅ Updated")

# ---------- DELETE ----------
st.markdown("### 🗑 Delete Row")

del_index = st.number_input("Enter Row Number to Delete", min_value=1, step=1, key="del")

if st.button("Delete Row"):
    if del_index <= len(df):
        df = df.drop(del_index-1).reset_index(drop=True)
        df.to_excel(FILE, index=False)
        st.warning("🗑 Deleted")

# ---------- DOWNLOAD EXCEL ----------
st.markdown("### 📥 Download")

buffer = BytesIO()
df.to_excel(buffer, index=False, engine='openpyxl')

st.download_button(
    label="📥 Download Excel",
    data=buffer.getvalue(),
    file_name="production.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# ---------- PDF ----------
if st.button("📄 Generate PDF"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=8)

    for i, row in df.iterrows():
        pdf.cell(200, 5, txt=str(row.values), ln=True)

    pdf.output("report.pdf")

    with open("report.pdf", "rb") as f:
        st.download_button("📄 Download PDF", f, file_name="report.pdf")
