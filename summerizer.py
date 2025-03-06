import streamlit as st
import os
import re
import requests
import tempfile
from youtube_transcript_api import YouTubeTranscriptApi
from langdetect import detect
import google.generativeai as genai
from dotenv import load_dotenv
from fpdf import FPDF

# Load environment variables and set up the API key
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to extract video ID from a YouTube URL
def extract_video_id(url):
    regex = r"(?:v=|\/|youtu\.be\/|embed\/|shorts\/)([0-9A-Za-z_-]{11})"
    match = re.search(regex, url)
    return match.group(1) if match else None

# Function to get the transcript of the YouTube video
def get_transcript(url):
    video_id = extract_video_id(url)
    if not video_id:
        return None, "Invalid YouTube URL."
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'hi'])
        transcript = " ".join([entry['text'] for entry in transcript_list])
        return transcript, None
    except Exception as e:
        return None, str(e)

# Function to generate key points from the transcript
def generate_keypoints(transcript):
    MAX_LENGTH = 3000  # Process only the first 3000 characters to reduce token usage
    if len(transcript) > MAX_LENGTH:
        transcript = transcript[:MAX_LENGTH] + "..."
    try:
        lang = detect(transcript)
    except Exception:
        lang = "en"
    # Simple and minimal prompt to generate bullet points in English
    prompt = f"Summarize the following YouTube video transcript into concise key bullet points in English:\n\n{transcript}"
    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt)
    return response.text

# Function to generate a PDF with the summary
def generate_pdf(summary):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "YouTube Video Key Points", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 10, summary)
    pdf_file = "youtube_summary.pdf"
    pdf.output(pdf_file)
    return pdf_file

# Streamlit UI
def main():
    st.title("YouTube Video Key Points Summarizer")
    youtube_url = st.text_input("Enter YouTube Video URL:")
    
    if youtube_url:
        video_id = extract_video_id(youtube_url)
        if video_id:
            thumbnail_url = f"http://img.youtube.com/vi/{video_id}/0.jpg"
            st.image(thumbnail_url, width=480)
        else:
            st.error("Invalid YouTube URL. Please check your link.")
    
    if st.button("Summarize Video"):
        if not youtube_url:
            st.error("Please enter a YouTube video URL.")
        else:
            with st.spinner("Fetching transcript..."):
                transcript, error = get_transcript(youtube_url)
            if error:
                st.error(f"Error fetching transcript: {error}")
            elif transcript:
                st.info("Transcript fetched successfully.")
                with st.spinner("Generating key points..."):
                    summary = generate_keypoints(transcript)
                    st.subheader("Key Points:")
                    st.write(summary)
                    st.session_state["summary"] = summary

    if st.button("Download Summary as PDF") and "summary" in st.session_state:
        pdf_file = generate_pdf(st.session_state["summary"])
        with open(pdf_file, "rb") as file:
            st.download_button("Download PDF", file, file_name="youtube_summary.pdf")

if __name__ == "__main__":
    main()
