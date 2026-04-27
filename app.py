import streamlit as st
import pandas as pd
from fpdf import FPDF
import os

FILE = "data.xlsx"

# Load data
if os.path.exists(FILE):
    df = pd.read_excel(FILE)
else:
    df = pd.DataFrame(columns=[
        "Day/Night","Machine","Size","Board type",
        "Thickness","Paper","Finish","osr",
        "A Grade","B Grade","Qty"
    ])

st.title("📊 Daily Production - Day & Night")

# Form
with st.form("entry_form"):
    col1, col2, col3 = st.columns(3)

    day = col1.selectbox("Day/Night", ["Day","Night"])
    machine = col2.text_input("Machine")
    size = col3.text_input("Size")

    board = col1.text_input("Board type")
    thickness = col2.text_input("Thickness")
    paper = col3.text_input("Paper")

    finish = col1.text_input("Finish")
    osr = col2.number_input("OSR", 0)
    a = col3.number_input("A Grade", 0)

    b = col1.number_input("B Grade", 0)
    qty = col2.number_input("Qty", 0)

    submit = st.form_submit_button("Save")

    if submit:
        new_row = pd.DataFrame([[day,machine,size,board,thickness,paper,finish,osr,a,b,qty]],
        columns=df.columns)

        df = pd.concat([df,new_row], ignore_index=True)
        df.to_excel(FILE, index=False)
        st.success("Saved!")

# Show table
st.subheader("📋 Data")
st.dataframe(df, use_container_width=True)

# Delete
row_delete = st.number_input("Delete Row No.", min_value=1, step=1)
if st.button("Delete"):
    df = df.drop(row_delete-1).reset_index(drop=True)
    df.to_excel(FILE, index=False)
    st.warning("Deleted!")

# Download Excel
st.download_button(
    "Download Excel",
    df.to_excel("temp.xlsx", index=False),
    file_name="production.xlsx"
)

# PDF
if st.button("Download PDF"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=8)

    for i, row in df.iterrows():
        pdf.cell(200, 5, txt=str(row.values), ln=True)

    pdf.output("report.pdf")
    with open("report.pdf", "rb") as f:
        st.download_button("Download PDF File", f, file_name="report.pdf")
