import streamlit as st
from PIL import Image
from paddleocr import PaddleOCR
import datetime
import pandas as pd
import io

st.title("📸 Gas Meter Reader (Cloud Compatible)")
st.write("Upload a gas meter photo. The app extracts the number and gives you an Excel file to download.")

# Initialize OCR
ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False)

# Upload
uploaded_file = st.file_uploader("Upload a gas meter photo", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded image", use_container_width=True)

    # Save image to bytes
    img_bytes = uploaded_file.read()

    # Run OCR
    result = ocr.ocr(img_bytes, cls=True)

    # Extract detected text
    extracted_text = [line[1][0] for line in result[0]] if result and result[0] else []
    st.write("🔍 OCR Results:", extracted_text)

    # Suggest first number
    default_reading = next((s for s in extracted_text if s.replace('.', '', 1).isdigit()), "")
    reading = st.text_input("Enter the correct gas meter reading:", value=default_reading)

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
