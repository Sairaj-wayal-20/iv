from dotenv import load_dotenv
import streamlit as st
import os
from PIL import Image
import pdf2image
from PyPDF2 import PdfReader
import google.generativeai as genai
from io import BytesIO

# Load environment variables
load_dotenv()

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to load OpenAI model and get responses
def get_gemini_response(input, image, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input, image[0], prompt])
    return response.text

# Function to set up image input
def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [{"mime_type": uploaded_file.type, "data": bytes_data}]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")

# Function to convert PDF to images and extract text
def process_pdf(uploaded_file):
    pdf_images = pdf2image.convert_from_bytes(uploaded_file.getvalue())
    pdf_reader = PdfReader(uploaded_file)
    pdf_text = ""

    for page in pdf_reader.pages:
        pdf_text += page.extract_text()

    image_parts = []
    for image in pdf_images:
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        image_parts.append({"mime_type": "image/png", "data": buffered.getvalue()})

    return pdf_text, image_parts

# Initialize Streamlit app
st.set_page_config(page_title="Gemini Image and PDF Demo")
st.header("Gemini Application")

input_text = st.text_input("Input Prompt: ", key="input")
uploaded_file = st.file_uploader("Choose an image or PDF...", type=["jpg", "jpeg", "png", "pdf"])

file_type = ""
if uploaded_file is not None:
    file_type = uploaded_file.type
    if "image" in file_type:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image.", use_column_width=True)
    elif "pdf" in file_type:
        pdf_text, pdf_images = process_pdf(uploaded_file)
        st.write("PDF Text Extracted:", pdf_text[:500], "...")  # Display first 500 characters

submit = st.button("Extract Information")

input_prompt = """
               You are an expert in understanding invoices.
               You will receive input images as invoices &
               you will have to answer questions based on the input image.
               """

# If submit button is clicked
if submit:
    if "image" in file_type:
        image_data = input_image_setup(uploaded_file)
        response = get_gemini_response(input_prompt, image_data, input_text)
    elif "pdf" in file_type:
        response = get_gemini_response(input_prompt, pdf_images, input_text + "\n" + pdf_text)
    
    st.subheader("The Response is")
    st.write(response)
