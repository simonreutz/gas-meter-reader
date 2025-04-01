import streamlit as st
import easyocr
import tempfile
import datetime
import pandas as pd
import io

# App title and description
st.title("📸 Gas Meter Reader (Offline Mode)")
st.write("Upload a gas meter photo. The app will extract the reading and let you download it as an Excel file.")

# Upload image
uploaded_file = st.file_uploader("Upload a gas meter photo", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # Show image
    st.image(uploaded_file, caption="Uploaded image", use_column_width=True)

    # Save temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    # OCR
    reader = easyocr.Reader(['en'], gpu=False)
    result = reader.readtext(tmp_path, detail=0)

    st.write("🔍 OCR Results:", result)

    # Ask user to confirm/correct
    default_reading = result[0] if result else ""
    reading = st.text_input("Enter the correct gas meter reading:", value=default_reading)

    last = st.number_input("Enter last month's reading", step=0.1)

    if st.button("📥 Generate Download"):
        try:
            usage = float(reading) - float(last)
            today = datetime.date.today()

            # Create a dataframe
            df = pd.DataFrame([{
                "Date": today,
                "Meter Reading": reading,
                "Monthly Usage": usage
            }])

            # Convert to Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Gas Log')
            excel_data = output.getvalue()

            # Download button
            st.download_button(
                label="📄 Download Excel File",
                data=excel_data,
                file_name=f"gas-log-{today}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            st.success("✅ Excel file ready for download!")

        except Exception as e:
            st.error(f"❌ Error: {e}")
