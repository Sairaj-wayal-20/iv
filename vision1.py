from dotenv import load_dotenv

load_dotenv()  # Take environment variables from .env.

import streamlit as st
import os
import textwrap
from PIL import Image
import pdf2image
from PyPDF2 import PdfReader

import google.generativeai as genai

os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

## Function to load OpenAI model and get response

def get_gemini_response(input, image, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input, image[0], prompt])
    return response.text

def convert_pdf_to_images(uploaded_file):
    images = pdf2image.convert_from_bytes(uploaded_file.read())
    image_parts = []
    for image in images:
        image_bytes = image.tobytes()
        image_parts.append({
            "mime_type": "image/jpeg",  # Assuming conversion to JPEG
            "data": image_bytes
        })
    return image_parts

def input_image_setup(uploaded_file):
    # Check if a file has been uploaded
    if uploaded_file is not None:
        if uploaded_file.type == "application/pdf":
            # Handle PDF files
            return convert_pdf_to_images(uploaded_file)
        else:
            # Handle image files
            bytes_data = uploaded_file.getvalue()
            image_parts = [
                {
                    "mime_type": uploaded_file.type,  # Get the mime type of the uploaded file
                    "data": bytes_data
                }
            ]
            return image_parts
    else:
        raise FileNotFoundError("No file uploaded")

## Initialize our Streamlit app

st.set_page_config(page_title="Gemini Image Demo")

st.header("Gemini Application")
input = st.text_input("Input Prompt: ", key="input")
uploaded_file = st.file_uploader("Choose an image or PDF...", type=["jpg", "jpeg", "png", "pdf"])
image = ""   
if uploaded_file is not None:
    if uploaded_file.type == "application/pdf":
        st.write("Uploaded PDF file.")
    else:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image.", use_column_width=True)

submit = st.button("Extract Information")

input_prompt = """
               You are an expert in understanding invoices.
               You will receive input images as invoices &
               you will have to answer questions based on the input image
               """

## If submit button is clicked

if submit:
    image_data = input_image_setup(uploaded_file)
    response = get_gemini_response(input_prompt, image_data, input)
    st.subheader("The Response is")
    st.write(response)
