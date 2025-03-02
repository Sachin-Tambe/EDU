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
            # URL to download NotoSans-Regular.ttf from a reliable source
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
    """Extracts video ID from different YouTube URL formats."""
    regex = r"(?:v=|\/|youtu\.be\/|embed\/|shorts\/)([0-9A-Za-z_-]{11})"
    match = re.search(regex, youtube_url)
    return match.group(1) if match else None

# Function to extract transcript from a YouTube video
def extract_transcript(youtube_url):
    try:
        video_id = extract_video_id(youtube_url)
        if not video_id:
            return "Error: Invalid YouTube URL."
        # Attempt to get transcript in English, fallback to Hindi if English is not available
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'hi'])
        transcript_text = " ".join([entry["text"] for entry in transcript_data])
        return transcript_text
    except Exception as e:
        return f"Error: {str(e)}"

# Function to generate summary using Gemini with language detection,
# but always returns the summary in English.
def generate_summary(transcript_text):
    try:
        detected_lang = detect(transcript_text)
    except Exception:
        detected_lang = 'en'  # Fallback to English if detection fails

    language_name = LANG_MAP.get(detected_lang, detected_lang)
    # Build a prompt that instructs the model to provide the summary in English
    prompt = (
        f"You are a YouTube video summarizer. The transcript text provided below is in {language_name}. "
        "Summarize the entire video in important points within 250 words. "
        "Provide the summary in English: "
    )
    
    model = genai.GenerativeModel("gemini-1.5-pro")  # Use the updated model name
    response = model.generate_content(prompt + transcript_text)
    return response.text

# Function to generate a PDF with the summary
def generate_pdf(content, youtube_url):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(200, 10, txt="YouTube Video Summary", ln=True, align='C')
    pdf.ln(10)

    video_id = extract_video_id(youtube_url)
    image_url = f"http://img.youtube.com/vi/{video_id}/0.jpg"
    temp_image_path = None
    image_y = 30
    image_height = 0

    try:
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_image:
                temp_image_path = temp_image.name
                for chunk in response.iter_content(1024):
                    temp_image.write(chunk)
            pdf.image(temp_image_path, x=15, y=image_y, w=180, h=100)
            image_height = 100
    except Exception:
        pdf.set_font("Arial", size=12)
        pdf.ln(20)
        pdf.cell(200, 10, txt="Error fetching video thumbnail.", ln=True, align='C')

    finally:
        if temp_image_path and os.path.exists(temp_image_path):
            os.remove(temp_image_path)

    pdf.set_y(image_y + image_height + 10)
    pdf.set_font("Arial", size=12)
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
        # For Q&A, concatenate the transcript with the question and generate an answer in English
        response = generate_summary(st.session_state["transcript_text"] + "\n" + user_question)
        st.write("**Answer:**", response)

    if st.button("Download Summary as PDF") and "summary" in st.session_state:
        pdf_file = generate_pdf(st.session_state["summary"], youtube_link)
        with open(pdf_file, "rb") as file:
            st.download_button("Download PDF", file, file_name="youtube_summary.pdf")

if __name__ == "__main__":
    main()
