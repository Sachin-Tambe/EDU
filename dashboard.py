import os
import streamlit as st
import time

# Attempt to import Google Generative AI (Palm) library
try:
    import google.generativeai as palm
except ImportError:
    palm = None

# ------------------- Configuration -------------------
# Set your Google Gen AI API key securely; replace "YOUR_API_KEY_HERE" or set the env variable.
API_KEY = os.getenv("GOOGLE_GEN_AI_API_KEY", "YOUR_API_KEY_HERE")
if palm is not None:
    try:
        palm.configure(api_key=API_KEY)
    except Exception as e:
        st.error(f"Error configuring Google Gen AI: {e}")

st.set_page_config(page_title="AI & Tech Dashboard", layout="wide")

# ------------------- Helper Functions -------------------
def refresh_page():
    """Refresh the page if supported; otherwise, prompt the user to manually refresh."""
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    else:
        st.warning("Refresh not supported in this version of Streamlit. Please reload your browser page to update content.")

def fetch_latest_news():
    """
    Fetch the latest AI and tech news using Google Generative AI.
    In production, replace the simulated response with an actual API call.
    """
    prompt = (
        "Provide a concise and updated summary of the latest news in the AI and tech industry. "
        "Include headlines on AI breakthroughs, newly launched AI tools, and major tech news, each with brief details."
    )
    if palm is not None and hasattr(palm, "generate_text"):
        try:
            response = palm.generate_text(
                prompt=prompt,
                temperature=0.7,
                max_output_tokens=300,
            )
            if response and hasattr(response, 'result') and response.result:
                return response.result.strip()
            else:
                return "No latest news available at the moment."
        except Exception as e:
            return f"Error fetching news: {e}"
    else:
        # Simulated news output
        return (
            "Simulated News:\n"
            "- AI Breakthrough: New NLP model sets benchmarks in understanding context.\n"
            "- Autonomous Systems: Reinforcement learning boosts self-driving technology.\n"
            "- Tech Update: Major smart device launch disrupts the market."
        )

def fetch_tech_stack_usage():
    """
    Fetch an analysis of the most popular tech stacks used in the industry using Google Generative AI.
    """
    prompt = (
        "Provide a detailed, bullet-point summary of the most popular tech stacks currently used in the industry. "
        "Include trends on programming languages, frameworks, and cloud platforms with available statistics."
    )
    if palm is not None and hasattr(palm, "generate_text"):
        try:
            response = palm.generate_text(
                prompt=prompt,
                temperature=0.7,
                max_output_tokens=300,
            )
            if response and hasattr(response, 'result') and response.result:
                return response.result.strip()
            else:
                return "No tech stack information available at the moment."
        except Exception as e:
            return f"Error fetching tech stack info: {e}"
    else:
        # Simulated tech stack insights
        return (
            "Simulated Tech Stack Insights:\n"
            "- Programming Languages: Python, JavaScript, and Java dominate.\n"
            "- Frameworks: React, Angular, Django, and Node.js are popular choices.\n"
            "- Cloud Platforms: AWS, GCP, and Azure lead the market."
        )

def fetch_industry_trends():
    """
    Fetch insights on the latest industry trends using Google Generative AI.
    """
    prompt = (
        "Provide an analysis of the latest industry trends in technology, including emerging technologies, market dynamics, "
        "and predictions for future innovations."
    )
    if palm is not None and hasattr(palm, "generate_text"):
        try:
            response = palm.generate_text(
                prompt=prompt,
                temperature=0.7,
                max_output_tokens=300,
            )
            if response and hasattr(response, 'result') and response.result:
                return response.result.strip()
            else:
                return "No industry trend information available at the moment."
        except Exception as e:
            return f"Error fetching industry trends: {e}"
    else:
        # Simulated industry trends
        return (
            "Simulated Industry Trends:\n"
            "- AI adoption continues to expand across multiple sectors.\n"
            "- Edge computing and IoT integration are on the rise.\n"
            "- Cybersecurity and data privacy remain critical priorities."
        )

# ------------------- Sidebar Navigation -------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select Section", [
    "Dashboard Overview", "Latest News", "Tech Stack Dashboard", "Industry Trends"
])

# ------------------- Dashboard Header -------------------
st.title("AI & Tech Dashboard")
st.markdown(
    """
Stay updated with the latest news in AI and technology and view dynamic insights on industry trends and tech stacks.  
Content is generated and updated dynamically via Google Generative AI.
    """
)

# ------------------- Page Content -------------------
if page == "Dashboard Overview":
    st.header("Dashboard Overview")
    st.markdown(
        "Welcome to the AI & Tech Dashboard. Use the sidebar to navigate between sections. "
        "Press the refresh buttons to update content when new information arrives."
    )
    if st.button("Refresh Dashboard"):
        refresh_page()

elif page == "Latest News":
    st.header("Latest News")
    with st.spinner("Fetching the latest news..."):
        news_content = fetch_latest_news()
    st.markdown(news_content)
    if st.button("Refresh News"):
        refresh_page()

elif page == "Tech Stack Dashboard":
    st.header("Tech Stack Dashboard")
    st.markdown(
        "Below is an analysis of the most popular tech stacks currently used in the industry, "
        "including trends on programming languages, frameworks, and cloud platforms."
    )
    with st.spinner("Fetching tech stack insights..."):
        tech_stack_info = fetch_tech_stack_usage()
    st.markdown(tech_stack_info)
    if st.button("Refresh Tech Stack Data"):
        refresh_page()

elif page == "Industry Trends":
    st.header("Industry Trends")
    st.markdown(
        "Get insights on the latest trends in the technology industry, including emerging technologies, market dynamics, "
        "and predictions for future innovations."
    )
    with st.spinner("Fetching industry trends..."):
        trends_info = fetch_industry_trends()
    st.markdown(trends_info)
    if st.button("Refresh Industry Trends"):
        refresh_page()
