import streamlit as st
from PIL import Image
import datetime
import pandas as pd
import io
import xlsxwriter

st.title("📸 Gas Meter Logger")
st.write("Upload a photo of your analog gas meter and log the reading — the image will be saved in the Excel file!")

uploaded_file = st.file_uploader("Upload your gas meter photo", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # Display uploaded image
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded image", use_container_width=True)

    # Manual entry
    reading = st.text_input("Enter your gas meter reading (from the image):")
    last = st.number_input("Enter last month's reading", step=0.1)

    if st.button("📥 Download Excel File"):
        try:
            usage = float(reading) - float(last)
            today = datetime.date.today()

            # Create output Excel in memory
            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output, {'in_memory': True})
            worksheet = workbook.add_worksheet("Gas Log")

            # Write table headers and values
            worksheet.write("A1", "Date")
            worksheet.write("B1", "Meter Reading")
            worksheet.write("C1", "Monthly Usage")

            worksheet.write("A2", str(today))
            worksheet.write("B2", reading)
            worksheet.write("C2", usage)

            # Resize and insert image into Excel
            image_buffer = io.BytesIO()
            image.save(image_buffer, format='PNG')
            image_buffer.seek(0)

            worksheet.insert_image("E1", "meter.png", {
                'image_data': image_buffer,
                'x_scale': 0.5,
                'y_scale': 0.5
            })

            workbook.close()
            output.seek(0)

            st.download_button(
                label="📄 Download Excel with Reading + Image",
                data=output,
                file_name=f"gas-log-{today}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            st.success("✅ Excel file with embedded image ready!")

        except Exception as e:
            st.error(f"❌ Error: {e}")
