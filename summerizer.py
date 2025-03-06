import streamlit as st
import re
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
from dotenv import load_dotenv
from fpdf import FPDF
import os

# Load environment variables and configure the API key for Google Generative AI
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to extract YouTube video ID from URL
def extract_video_id(url):
    regex = r"(?:v=|\/|youtu\.be\/|embed\/|shorts\/)([0-9A-Za-z_-]{11})"
    match = re.search(regex, url)
    return match.group(1) if match else None

# Function to fetch transcript using youtube_transcript_api
def fetch_transcript(youtube_url):
    video_id = extract_video_id(youtube_url)
    if not video_id:
        return None, "Invalid YouTube URL."
    try:
        # Try fetching transcript in English; a fallback language can be added if needed
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=["en", "hi"])
        transcript = " ".join([entry["text"] for entry in transcript_list])
        return transcript, None
    except Exception as e:
        return None, str(e)

# Function to generate key point summary using Google Generative AI
def generate_summary(transcript):
    MAX_LENGTH = 3000  # Truncate transcript to limit token usage
    if len(transcript) > MAX_LENGTH:
        transcript = transcript[:MAX_LENGTH] + "..."
    prompt = f"Summarize the following YouTube video transcript into concise key bullet points in English:\n\n{transcript}"
    model = genai.GenerativeModel("gemini-1.5-pro")
    try:
        response = model.generate_content(prompt)
        summary = response.text
        if not summary:
            return None, "No summary generated."
        return summary, None
    except Exception as e:
        return None, str(e)

# Function to generate a PDF from the summary text
def generate_pdf(summary):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "YouTube Video Key Points", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, summary)
    pdf_file = "youtube_summary.pdf"
    pdf.output(pdf_file)
    return pdf_file

# Main Streamlit UI
def main():
    st.title("YouTube Video Summarizer")
    youtube_url = st.text_input("Enter YouTube Video URL:")
    
    if youtube_url:
        video_id = extract_video_id(youtube_url)
        if video_id:
            thumbnail_url = f"http://img.youtube.com/vi/{video_id}/0.jpg"
            st.image(thumbnail_url, width=480)
        else:
            st.error("Invalid YouTube URL.")
    
    if st.button("Summarize Video"):
        if not youtube_url:
            st.error("Please enter a YouTube video URL.")
            return
        
        with st.spinner("Fetching transcript..."):
            transcript, error = fetch_transcript(youtube_url)
        if error:
            st.error(f"Error fetching transcript: {error}")
            return
        
        st.success("Transcript fetched successfully.")
        st.text_area("Transcript (truncated):", transcript[:500] + "..." if len(transcript) > 500 else transcript, height=150)
        
        with st.spinner("Generating summary key points..."):
            summary, error = generate_summary(transcript)
        if error:
            st.error(f"Error generating summary: {error}")
            return
        
        st.subheader("Key Points:")
        st.write(summary)
        st.session_state["summary"] = summary

    if st.button("Download Summary as PDF") and "summary" in st.session_state:
        pdf_file = generate_pdf(st.session_state["summary"])
        with open(pdf_file, "rb") as f:
            st.download_button("Download PDF", f, file_name="youtube_summary.pdf")

if __name__ == "__main__":
    main()
