import streamlit as st
import os
import google.generativeai as genai
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import numpy as np

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Quiz Generation Prompt
quiz_prompt = """Generate {num_questions} multiple-choice questions on {topic}.
Each question should have 4 options and 1 correct answer. Format:

1. Question?
   a) Option 1
   b) Option 2
   c) Option 3
   d) Option 4
   Answer: (correct option letter)
"""

def generate_quiz(topic, num_questions):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(quiz_prompt.format(topic=topic, num_questions=num_questions))
    return response.text

def extract_text_from_pdf(pdf):
    text = ""
    pdf_reader = PdfReader(pdf)
    for page in pdf_reader.pages:
        if page.extract_text():
            text += page.extract_text() + "\n"
    return text.strip()

def parse_quiz_response(response):
    questions = []
    current_question = None  # Start with no active question
    
    for line in response.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        # Detect question start (ensuring a valid split)
        if line[0].isdigit() and '.' in line:
            if current_question:
                questions.append(current_question)
            current_question = {
                'question': line.split('. ', 1)[1] if '. ' in line else line,
                'options': [],
                'answer': ''
            }
        
        # Detect option (ensuring the key exists)
        elif line.lower().startswith(('a)', 'b)', 'c)', 'd)')) and current_question is not None:
            if 'options' not in current_question:
                current_question['options'] = []
            current_question['options'].append(line)
        
        # Detect answer
        elif line.lower().startswith('answer:') and current_question is not None:
            answer = line.split(':')[-1].strip().lower()
            current_question['answer'] = answer[0] if answer else ''

    # Append the last question if it exists
    if current_question:
        questions.append(current_question)
    
    return questions


def quiz_app():
    st.subheader("📝 Quiz Generator")

    # Choose Input Source
    quiz_source = st.radio("Choose Input Source:", ("Topic Name", "Upload PDF"))
    
    topic = ""
    if quiz_source == "Topic Name":
        topic = st.text_input("Enter a topic:")
    else:
        uploaded_pdf = st.file_uploader("Upload a PDF", type=["pdf"])
        if uploaded_pdf:
            topic = extract_text_from_pdf(uploaded_pdf)

    num_questions = st.number_input("Enter number of questions:", min_value=1, max_value=20, value=5)

    if st.button("Generate Quiz"):
        if topic.strip():
            quiz_response = generate_quiz(topic, num_questions)
            parsed_questions = parse_quiz_response(quiz_response)
            
            # Initialize session state
            st.session_state['quiz_data'] = parsed_questions
            st.session_state['user_answers'] = {}
            st.session_state['show_results'] = False

    if 'quiz_data' in st.session_state:
        for idx, question_data in enumerate(st.session_state['quiz_data']):
            st.write(f"**Q{idx + 1}: {question_data['question']}**")
            
            # Extract option text and letters separately
            options = [opt.split(') ', 1)[1] for opt in question_data['options']]
            option_letters = [opt[0].lower() for opt in question_data['options']]
            
            # Get user's previous answer if exists
            previous_answer = st.session_state['user_answers'].get(idx, None)
            
            user_answer = st.radio(
                f"Choose your answer for Q{idx + 1}:",
                options=options,
                index=option_letters.index(previous_answer) if previous_answer in option_letters else None,
                key=f"q{idx}",
                format_func=lambda x: x
            )
            
            # Store the letter answer
            if user_answer:
                selected_index = options.index(user_answer)
                st.session_state['user_answers'][idx] = option_letters[selected_index]

        if st.button("Submit Answers"):
            st.session_state['show_results'] = True

        if st.session_state.get('show_results', False):
            correct_count = 0
            results = []
            
            for idx, question_data in enumerate(st.session_state['quiz_data']):
                user_answer = st.session_state['user_answers'].get(idx, 'No answer')
                correct_answer = question_data['answer'].lower()
                is_correct = user_answer == correct_answer
                
                if is_correct:
                    correct_count += 1
                
                results.append({
                    'question': question_data['question'],
                    'user_answer': user_answer.upper() if user_answer != 'No answer' else user_answer,
                    'correct_answer': correct_answer.upper(),
                    'is_correct': is_correct
                })
            
            st.subheader("Results")
            st.write(f"✅ Correct: {correct_count}/{len(results)}")
            st.write(f"❌ Incorrect: {len(results) - correct_count}/{len(results)}")

            # Visualization Section
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            
            # Pie Chart
            labels = ['Correct', 'Incorrect']
            sizes = [correct_count, len(results)-correct_count]
            colors = ['#4CAF50', '#F44336']
            ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            ax1.set_title('Score Distribution')

            # Bar Chart
            question_numbers = [f'Q{i+1}' for i in range(len(results))]
            correctness = [1 if res['is_correct'] else 0 for res in results]
            bar_colors = [colors[0] if c == 1 else colors[1] for c in correctness]
            ax2.bar(question_numbers, correctness, color=bar_colors)
            ax2.set_title('Question-wise Performance')
            ax2.set_ylim(0, 1)
            ax2.set_yticks([0, 1])
            ax2.set_yticklabels(['Incorrect', 'Correct'])
            
            plt.tight_layout()
            st.pyplot(fig)

            # Detailed Results
            st.subheader("Detailed Breakdown")
            for idx, result in enumerate(results):
                st.write(f"**Q{idx + 1}: {result['question']}**")
                st.write(f"Your answer: {result['user_answer']}")
                st.write(f"Correct answer: {result['correct_answer']}")
                st.write("Result: " + ("✅ Correct" if result['is_correct'] else "❌ Incorrect"))
                st.write("---")

if __name__ == "__main__":
    st.set_page_config(page_title="Quiz Generator", layout="wide")
    st.title("📝 Quiz Generator with Performance Analytics")
    quiz_app()