import streamlit as st
import pandas as pd
from datetime import datetime
import os
# -----------------------
# SIMPLE LOGIN SYSTEM
# -----------------------

USERNAME = "admin"
PASSWORD = "1234"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.title("🔐 Login Required")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == USERNAME and password == PASSWORD:
            st.session_state.logged_in = True
            st.success("Login Successful!")
            st.rerun()
        else:
            st.error("Wrong Username or Password")

if not st.session_state.logged_in:
    login()
    st.stop()
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import pagesizes

st.set_page_config(page_title="Production Report", layout="wide")

DATA_FILE = "data.csv"

# Load data
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=[
        "Date","Shift","Machine","Size","Board","Thickness",
        "Paper","Finish","OSR","Agrade","Bgrade","Grand Total"
    ])

st.title("📋 Production Entry")

# ---------------------------
# DATE + SHIFT SIDE BY SIDE
# ---------------------------
col1, col2 = st.columns(2)

with col1:
    report_date = st.date_input("Date", datetime.today())

with col2:
    shift = st.selectbox("Shift", ["Morning","Evening","Night"])

# ---------------------------
# MACHINE
# ---------------------------
machines = ["Machine 1","Machine 2","Machine 3","Machine 4","Machine 5"]
machine = st.selectbox("Machine No", machines)

# ---------------------------
# DETAILS
# ---------------------------
size = st.text_input("Size")
board = st.text_input("Board")
thickness = st.text_input("Thickness")
paper = st.text_input("Paper")
finish = st.text_input("Finish")

# ---------------------------
# PRODUCTION NUMBERS
# ---------------------------
osr = st.text_input("OSR")
agrade = st.text_input("A Grade")
bgrade = st.text_input("B Grade")

# Calculate Total
try:
    total = float(osr or 0) + float(agrade or 0) + float(bgrade or 0)
except:
    total = 0

st.markdown(f"### Grand Total: {total}")

# ---------------------------
# SAVE BUTTON
# ---------------------------
if st.button("Save Entry"):

    new_row = {
        "Date": report_date,
        "Shift": shift,
        "Machine": machine,
        "Size": size,
        "Board": board,
        "Thickness": thickness,
        "Paper": paper,
        "Finish": finish,
        "OSR": osr,
        "Agrade": agrade,
        "Bgrade": bgrade,
        "Grand Total": total
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    st.success("Entry Saved Successfully!")

# ---------------------------
# REPORT SECTION
# ---------------------------
st.markdown("## 📊 Production Report")

if df.empty:
    st.info("No data available.")
else:

    # Show full table
    st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.markdown("### Select Entry to Edit or Delete")

    # Create selection list
    selection = st.selectbox(
        "Select Entry",
        df.index,
        format_func=lambda x: f"{df.loc[x,'Date']} | {df.loc[x,'Machine']} | Total: {df.loc[x,'Grand Total']}"
    )

    row = df.loc[selection]

    st.markdown("### ✏️ Edit Entry")

    col1, col2 = st.columns(2)

    with col1:
        new_size = st.text_input("Size", row["Size"])
        new_board = st.text_input("Board", row["Board"])
        new_osr = st.text_input("OSR", row["OSR"])

    with col2:
        new_agrade = st.text_input("A Grade", row["Agrade"])
        new_bgrade = st.text_input("B Grade", row["Bgrade"])

    try:
        new_total = float(new_osr or 0) + float(new_agrade or 0) + float(new_bgrade or 0)
    except:
        new_total = 0

    st.write("Updated Total:", new_total)

    col3, col4 = st.columns(2)

    if col3.button("Update Entry"):
        df.at[selection, "Size"] = new_size
        df.at[selection, "Board"] = new_board
        df.at[selection, "OSR"] = new_osr
        df.at[selection, "Agrade"] = new_agrade
        df.at[selection, "Bgrade"] = new_bgrade
        df.at[selection, "Grand Total"] = new_total

        df.to_csv(DATA_FILE, index=False)
        st.success("Updated Successfully!")
        st.rerun()

    if col4.button("Delete Entry"):
        df = df.drop(selection)
        df.to_csv(DATA_FILE, index=False)
        st.warning("Deleted Successfully!")
        st.rerun()
    # CSV Download
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "report.csv", "text/csv")

    # Excel Download
    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False)
    st.download_button(
        "Download Excel",
        excel_buffer.getvalue(),
        "report.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # PDF Download
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=pagesizes.A4)
    elements = []

    table_data = [df.columns.tolist()] + df.values.tolist()
    table = Table(table_data)
    table.setStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black)
    ])

    elements.append(table)
    doc.build(elements)

    st.download_button(
        "Download PDF",
        pdf_buffer.getvalue(),
        "report.pdf",
        "application/pdf"
    )


    st.info("No data available.")
