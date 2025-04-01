import streamlit as st
from PIL import Image
import pytesseract
import datetime
import pandas as pd
import io

st.title("📸 Gas Meter Reader (Light Version)")
st.write("Upload a gas meter photo. The app will extract the number and let you download it as Excel.")

uploaded_file = st.file_uploader("Upload a gas meter photo", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")  # Ensure image is in correct format
    st.image(image, caption="Uploaded image", use_container_width=True)

    text = pytesseract.image_to_string(image)
    st.write("🔍 Raw OCR Text:", text)

    reading = st.text_input("Enter the gas meter reading:", value=text.strip())

    last = st.number_input("Enter last month's reading", step=0.1)

    if st.button("📥 Download Excel File"):
        usage = float(reading) - float(last)
        today = datetime.date.today()

        df = pd.DataFrame([{
            "Date": today,
            "Meter Reading": reading,
            "Monthly Usage": usage
        }])

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Gas Log')
        excel_data = output.getvalue()

        st.download_button(
            label="📄 Download Excel File",
            data=excel_data,
            file_name=f"gas-log-{today}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.success("✅ File ready for download!")
