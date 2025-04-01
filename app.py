import streamlit as st
import easyocr
from PIL import Image
import tempfile
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Title
st.title("📸 Gas Meter Reader")
st.write("Upload a photo of your analog gas meter. The app will extract the value and log it to your Google Sheet.")

# Image upload
uploaded_file = st.file_uploader("Upload meter photo", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="Uploaded image", use_column_width=True)

    # Save to temp file for OCR
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        img.save(tmp.name)
        reader = easyocr.Reader(['en'])
        result = reader.readtext(tmp.name, detail=0)
    
    st.write("🔍 OCR Results:", result)
    reading = st.text_input("Enter correct gas meter reading from image:", value=result[0] if result else "")

    last = st.number_input("Enter last month's reading (for usage calculation)", step=0.1)

    if st.button("Save to Google Sheets"):
        # Calculate usage
        usage = float(reading) - float(last)

        # Google Sheets connection
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
        client = gspread.authorize(creds)

        sheet = client.open("Gas Usage Tracker").sheet1
        sheet.append_row([str(datetime.date.today()), reading, usage])

        st.success("✅ Logged to Google Sheets!")
