import streamlit as st
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from fpdf import FPDF
import requests
from dotenv import load_dotenv
import tempfile
import re
from langdetect import detect

# Load environment variables and configure API key
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Language mapping
LANG_MAP = {
    'en': 'English',
    'hi': 'Hindi'
}

# Ensure NotoSans font file exists
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

# Extract YouTube video ID from URL
def extract_video_id(youtube_url):
    regex = r"(?:v=|\/|youtu\.be\/|embed\/|shorts\/)([0-9A-Za-z_-]{11})"
    match = re.search(regex, youtube_url)
    return match.group(1) if match else None

# Extract transcript from YouTube video
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

# Constants to control token usage
MAX_TRANSCRIPT_LENGTH = 5000  # Process only first 5000 characters of transcript
MAX_CHUNK_SIZE = 1500         # Process in chunks of 1500 characters

# Generate summary with optimized token usage
def generate_summary(transcript_text):
    # Truncate transcript to maximum allowed length
    if len(transcript_text) > MAX_TRANSCRIPT_LENGTH:
        transcript_text = transcript_text[:MAX_TRANSCRIPT_LENGTH] + "..."
    
    try:
        detected_lang = detect(transcript_text)
    except Exception:
        detected_lang = 'en'
    language_name = LANG_MAP.get(detected_lang, detected_lang)
    
    model = genai.GenerativeModel("gemini-1.5-pro")
    
    # Agar transcript lamba hai to chhote chunks mein baantein
    if len(transcript_text) > MAX_CHUNK_SIZE:
        chunks = [transcript_text[i:i+MAX_CHUNK_SIZE] for i in range(0, len(transcript_text), MAX_CHUNK_SIZE)]
        partial_summaries = []
        for chunk in chunks:
            prompt = (
                f"Summarize the following transcript in bullet points in English (max 150 words):\n\n{chunk}"
            )
            response = model.generate_content(prompt)
            partial_summaries.append(response.text)
        combined_summary = "\n".join(partial_summaries)
        final_prompt = (
            "Combine the following summaries into a concise overall summary in bullet points in English (max 250 words):\n\n"
            f"{combined_summary}"
        )
        final_response = model.generate_content(final_prompt)
        return final_response.text
    else:
        prompt = (
            f"Summarize the following transcript in bullet points in English (max 250 words):\n\n{transcript_text}"
        )
        response = model.generate_content(prompt)
        return response.text

# Generate answer for user question with optimized prompt
def generate_answer(transcript_text, user_question):
    # Agar transcript lamba ho to uska concise summary generate karke use context ke roop mein use karein
    if len(transcript_text) > MAX_TRANSCRIPT_LENGTH:
        transcript_context = generate_summary(transcript_text)
    else:
        transcript_context = transcript_text

    prompt = (
        "Based on the following transcript summary, answer the question in clear, concise English:\n\n"
        f"Transcript Summary:\n{transcript_context}\n\n"
        f"Question: {user_question}\n\n"
        "Answer:"
    )
    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt)
    return response.text

# Generate PDF of the summary
def generate_pdf(content, youtube_url):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Add custom font
    font_path = ensure_font_file()
    try:
        pdf.add_font("NotoSans", "", font_path, uni=True)
        font_name = "NotoSans"
    except Exception:
        font_name = "Arial"

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
        except Exception:
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
