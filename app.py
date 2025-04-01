import streamlit as st
from PIL import Image
import datetime
import pandas as pd
import io

st.title("📸 Gas Meter Logger")
st.write("Upload a gas meter photo and log your reading. No OCR needed!")

uploaded_file = st.file_uploader("Upload your gas meter photo", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # Show the image
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded image", use_container_width=True)

    # Ask user to input manually
    reading = st.text_input("Enter your gas meter reading (from the image):")
    last = st.number_input("Enter last month's reading", step=0.1)

    if st.button("📥 Download Excel File"):
        try:
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

            st.success("✅ File ready to download!")

        except Exception as e:
            st.error(f"❌ Something went wrong: {e}")
