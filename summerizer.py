import streamlit as st
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from fpdf import FPDF
import requests
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Summary prompt
summary_prompt = """You are a YouTube video summarizer. Given the transcript text,
summarize the entire video in important points within 250 words. Provide the summary for the text given here: """

# Function to extract transcript from YouTube video
def extract_transcript(youtube_url):
    try:
        video_id = youtube_url.split("v=")[-1]
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id)

        transcript_text = " ".join([entry["text"] for entry in transcript_data])
        return transcript_text
    except Exception as e:
        return f"Error: {str(e)}"

# Function to generate summary using Gemini
def generate_summary(transcript_text):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(summary_prompt + transcript_text)
    return response.text

import tempfile
import os

def generate_pdf(content, youtube_url):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title at the top
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(200, 10, txt="YouTube Video Summary", ln=True, align='C')
    pdf.ln(10)  # Space after title

    video_id = youtube_url.split("v=")[-1]
    image_url = f"http://img.youtube.com/vi/{video_id}/0.jpg"

    temp_image_path = None  # Store image path

    try:
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_image:
                temp_image_path = temp_image.name
                for chunk in response.iter_content(1024):
                    temp_image.write(chunk)

            # Insert image into PDF
            image_x = 15
            image_y = 30
            image_width = 180
            image_height = 100  # Adjust height dynamically if needed

            pdf.image(temp_image_path, x=image_x, y=image_y, w=image_width, h=image_height)

        else:
            raise Exception("Failed to fetch image")

    except Exception as e:
        pdf.set_font("Arial", size=12)
        pdf.ln(20)
        pdf.cell(200, 10, txt="Error fetching video thumbnail.", ln=True, align='C')

    finally:
        # Clean up temporary image file
        if temp_image_path and os.path.exists(temp_image_path):
            os.remove(temp_image_path)

    # Move the text **below the image dynamically**
    pdf.set_y(image_y + image_height + 10)  # Ensure text starts after image
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
        video_id = youtube_link.split("v=")[-1]
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

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
        response = generate_summary(st.session_state["transcript_text"] + "\n" + user_question)
        st.write("**Answer:**", response)

    if st.button("Download Summary as PDF") and "summary" in st.session_state:
        pdf_file = generate_pdf(st.session_state["summary"], youtube_link)
        with open(pdf_file, "rb") as file:
            st.download_button("Download PDF", file, file_name="youtube_summary.pdf")

if __name__ == "__main__":
    main()
