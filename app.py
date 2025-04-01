import streamlit as st
import easyocr
import tempfile
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# App title and instructions
st.title("📸 Gas Meter Reader")
st.write("Upload a photo of your analog gas meter. The app will extract the number using OCR and log it to your Google Sheet.")

# Upload image
uploaded_file = st.file_uploader("Upload a gas meter photo", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # Display uploaded image
    st.image(uploaded_file, caption="Uploaded image", use_column_width=True)

    # Save uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_file_path = tmp_file.name

    # Run OCR on the saved image
    reader = easyocr.Reader(['en'], gpu=False)
    result = reader.readtext(tmp_file_path, detail=0)

    # Show raw OCR results
    st.write("🔍 OCR Results:", result)

    # Get first result as default suggestion
    default_reading = result[0] if result else ""
    reading = st.text_input("Enter the correct gas meter reading from image:", value=default_reading)

    # Ask for previous reading
    last = st.number_input("Enter last month's reading", step=0.1)

    # Save to Google Sheets
    if st.button("📤 Save to Google Sheets"):
        try:
            usage = float(reading) - float(last)

            # Google Sheets auth using secrets
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            creds_dict = json.loads(st.secrets["general"]["GOOGLE_SHEETS_CREDS"])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            client = gspread.authorize(creds)

            # Append data to the first worksheet
            sheet = client.open("Gas Usage Tracker").sheet1
            sheet.append_row([str(datetime.date.today()), reading, usage])

            # Success message
            st.success("✅ Entry saved to Google Sheets!")
            st.write(f"**Date:** {datetime.date.today()}  \n**Reading:** {reading}  \n**Monthly Usage:** {usage:.2f}")
        except Exception as e:
            st.error(f"❌ Failed to save entry: {e}")
