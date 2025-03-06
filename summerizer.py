import streamlit as st
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from fpdf import FPDF
import requests
from io import BytesIO
from dotenv import load_dotenv
import tempfile
import re
from langdetect import detect

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Mapping for language codes to human-readable names
LANG_MAP = {
    'en': 'English',
    'hi': 'Hindi'
    # Extend with other language codes as needed.
}

# Helper function to ensure the NotoSans-Regular.ttf file is present
def ensure_font_file():
    font_path = "NotoSans-Regular.ttf"
    if not os.path.exists(font_path):
        try:
            font_url = "https://raw.githubusercontent.com/codertimo/FPDF/master/font/NotoSans-Regular.ttf"
            response = requests.get(font_url)
            response.raise_for_status()
            with open(font_path, "wb") as f:
                f.write(response.content)
            st.info("Downloaded NotoSans-Regular.ttf successfully.")
        except Exception as e:
            st.error(f"Failed to download NotoSans-Regular.ttf: {e}")
    return font_path

# Function to extract video ID from YouTube URL
def extract_video_id(youtube_url):
    regex = r"(?:v=|\/|youtu\.be\/|embed\/|shorts\/)([0-9A-Za-z_-]{11})"
    match = re.search(regex, youtube_url)
    return match.group(1) if match else None

# Function to extract transcript from a YouTube video
def extract_transcript(youtube_url):
    try:
        video_id = extract_video_id(youtube_url)
        if not video_id:
            return "Error: Invalid YouTube URL."
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'hi'])
        transcript_text = " ".join([entry["text"] for entry in transcript_data])
        return transcript_text
    except Exception as e:
        return f"Error: {str(e)}"

# Function to generate summary using Gemini
def generate_summary(transcript_text):
    try:
        detected_lang = detect(transcript_text)
    except Exception:
        detected_lang = 'en'
    language_name = LANG_MAP.get(detected_lang, detected_lang)
    prompt = (
        f"You are a YouTube video summarizer. The transcript text provided below is in {language_name}. "
        "Summarize the entire video in important points within 250 words. Provide the summary in English:\n\n"
        f"{transcript_text}"
    )
    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt)
    return response.text

# Function to generate an answer for user questions based on the transcript
def generate_answer(transcript_text, user_question):
    try:
        detected_lang = detect(transcript_text)
    except Exception:
        detected_lang = 'en'
    language_name = LANG_MAP.get(detected_lang, detected_lang)
    prompt = (
        f"You are a YouTube video assistant. The transcript below is in {language_name}. "
        "Based on the transcript, answer the following question in clear English.\n\n"
        f"Transcript:\n{transcript_text}\n\n"
        f"Question: {user_question}\n\n"
        "Answer:"
    )
    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt)
    return response.text

# Function to generate a PDF with the summary
def generate_pdf(content, youtube_url):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Ensure font file and add font
    font_path = ensure_font_file()
    try:
        pdf.add_font("NotoSans", "", font_path, uni=True)
        font_name = "NotoSans"
    except Exception as e:
        font_name = "Arial"

    # Title
    pdf.set_font(font_name, style='B', size=16)
    pdf.cell(200, 10, txt="YouTube Video Summary", ln=True, align='C')
    pdf.ln(10)

    video_id = extract_video_id(youtube_url)
    if video_id:
        image_url = f"http://img.youtube.com/vi/{video_id}/0.jpg"
        try:
            response = requests.get(image_url, stream=True, timeout=10)
            response.raise_for_status()
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_image:
                temp_image.write(response.content)
                temp_image_path = temp_image.name
            pdf.image(temp_image_path, x=15, y=30, w=180, h=100)
            os.remove(temp_image_path)
        except Exception as e:
            pdf.set_font(font_name, size=12)
            pdf.ln(20)
            pdf.cell(200, 10, txt="Error fetching video thumbnail.", ln=True, align='C')

    pdf.set_y(140)
    pdf.set_font(font_name, size=12)
    pdf.multi_cell(0, 10, content)

    pdf_output_path = "youtube_summary.pdf"
    pdf.output(pdf_output_path)
    return pdf_output_path

# Streamlit UI
def main():
    st.set_page_config(page_title="YouTube Summarizer")
    st.title("YouTube Video Summarizer 🎥📄")

    youtube_link = st.text_input("Enter YouTube Video Link:")
    if youtube_link:
        video_id = extract_video_id(youtube_link)
        if video_id:
            st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)
        else:
            st.error("Invalid YouTube URL. Please enter a valid link.")

    if st.button("Summarize Video"):
        if not youtube_link:
            st.error("Please enter a YouTube video link.")
        else:
            with st.spinner("Fetching transcript and summarizing..."):
                transcript_text = extract_transcript(youtube_link)
                if transcript_text.startswith("Error"):
                    st.error(transcript_text)
                else:
                    summary = generate_summary(transcript_text)
                    st.session_state["transcript_text"] = transcript_text
                    st.session_state["summary"] = summary
                    st.write(summary)

    user_question = st.text_input("Ask a question about the video:")
    if user_question and "transcript_text" in st.session_state:
        with st.spinner("Generating answer..."):
            answer = generate_answer(st.session_state["transcript_text"], user_question)
            st.write("**Answer:**", answer)

    if st.button("Download Summary as PDF") and "summary" in st.session_state:
        pdf_file = generate_pdf(st.session_state["summary"], youtube_link)
        with open(pdf_file, "rb") as file:
            st.download_button("Download PDF", file, file_name="youtube_summary.pdf")

if __name__ == "__main__":
    main()
