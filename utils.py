# utils.py

import PyPDF2 as pdf
import docx
import streamlit as st
import base64
import io
import zipfile

def get_text_from_files(uploaded_files):
    """
    Reads and extracts text from a list of uploaded files (PDF, DOCX, TXT).
    """
    full_text = ""
    for file in uploaded_files:
        if file.type == "application/pdf":
            pdf_reader = pdf.PdfReader(file)
            for page in pdf_reader.pages:
                full_text += page.extract_text() or ""
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = docx.Document(file)
            for para in doc.paragraphs:
                full_text += para.text + "\n"
        elif file.type == "text/plain":
            full_text += file.getvalue().decode("utf-8") + "\n"
    return full_text


def create_download_link(text_content, filename):
    """
    Generates a download link for a DOCX file created from text content.
    """
    # Create a document object
    doc = docx.Document()
    doc.add_paragraph(text_content)
    
    # Save the document to a byte stream
    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    
    # Encode the byte stream to base64
    b64 = base64.b64encode(bio.read()).decode()
    
    # Create the download link
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{b64}" download="{filename}.docx">Download Your Resume as DOCX</a>'
    return href


def process_zip_file(uploaded_zip_file):
    """
    Extracts text from all supported files (PDF, DOCX, TXT) within a ZIP archive.
    Returns a dictionary where keys are filenames and values are the extracted text.
    """
    extracted_texts = {}
    with zipfile.ZipFile(uploaded_zip_file, 'r') as zip_ref:
        for file_info in zip_ref.infolist():
            # Skip directories and hidden files
            if file_info.is_dir() or file_info.filename.startswith('__MACOSX'):
                continue

            filename = file_info.filename
            file_extension = filename.split('.')[-1].lower()

            with zip_ref.open(file_info) as file_in_zip:
                # Wrap the file in a BytesIO stream to make it compatible with our existing functions
                file_stream = io.BytesIO(file_in_zip.read())

                if file_extension == 'pdf':
                    try:
                        pdf_reader = pdf.PdfReader(file_stream)
                        text = ""
                        for page in pdf_reader.pages:
                            text += page.extract_text() or ""
                        extracted_texts[filename] = text
                    except Exception as e:
                        extracted_texts[filename] = f"Error reading PDF: {e}"

                elif file_extension == 'docx':
                    try:
                        doc = docx.Document(file_stream)
                        text = "\n".join([para.text for para in doc.paragraphs])
                        extracted_texts[filename] = text
                    except Exception as e:
                        extracted_texts[filename] = f"Error reading DOCX: {e}"
                
                elif file_extension == 'txt':
                    try:
                        text = file_stream.getvalue().decode("utf-8")
                        extracted_texts[filename] = text
                    except Exception as e:
                        extracted_texts[filename] = f"Error reading TXT: {e}"

    return extracted_texts