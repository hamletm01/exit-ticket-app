import streamlit as st
from google import genai

# Page Configuration
st.set_page_config(page_title="AI Exit Ticket", page_icon="🎓")

st.title("🎓 Adaptive Lesson Exit Ticket")
st.write("Complete today's exit ticket to check your understanding!")

# 1. Access & Clean Gemini API Key from Streamlit Secrets
if "GEMINI_API_KEY" in st.secrets:
    api_key = str(st.secrets["GEMINI_API_KEY"]).strip().strip('"').strip("'")
    client = genai.Client(api_key=api_key)
else:
    st.error("API Key not found. Please configure GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

# Current Active Gemini Model
MODEL_NAME = "gemini-3.6-flash"

# 2. Teacher Setup Area (Sidebar)
with st.sidebar:
    st.header("👨‍🏫 Teacher Setup")
    lesson_notes = st.text_area("Paste Today's Lesson Content / Notes:", height=200)
    generate_btn = st.button("Generate Exit Ticket")

# Session State to hold generated questions
if "questions" not in st.session_state:
    st.session_state.questions = None

# Generate Questions using Gemini
if generate_btn and lesson_notes:
    with st.spinner("Generating questions from lesson content..."):
        try:
            prompt = f"""
            You are a high school teacher in Australia. Based on the following lesson notes, 
            generate exactly 3 short-answer exit ticket questions to test student comprehension:
            
            Lesson Notes:
            {lesson_notes}
            
            Format your response cleanly with Question 1, Question 2, and Question 3.
            """
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
            )
            st.session_state.questions = response.text
            st.success("Exit Ticket Created!")
        except Exception as e:
            st.error(f"Error generating questions: {e}")

# 3. Student View
if st.session_state.questions:
    st.subheader("Today's Questions")
    st.write(st.session_state.questions)
    
    student_id = st.text_input("Enter your Name or Student ID:")
    ans1 = st.text_area("Answer to Question 1:")
    ans2 = st.text_area("Answer to Question 2:")
    ans3 = st.text_area("Answer to Question 3:")
    
    if st.button("Submit Answers"):
        if student_id and ans1 and ans2 and ans3:
            with st.spinner("Evaluating your responses..."):
                try:
                    eval_prompt = f"""
                    You are a supportive high school tutor. Grade these student answers based on the original lesson content.
                    
                    Lesson Content: {lesson_notes}
                    Questions: {st.session_state.questions}
                    Student Answers:
                    1. {ans1}
                    2. {ans2}
                    3. {ans3}
                    
                    Provide:
                    1. Brief feedback on what they got right.
                    2. Friendly diagnostic advice on what concepts they need to revise before next lesson.
                    """
                    feedback = client.models.generate_content(
                        model=MODEL_NAME,
                        contents=eval_prompt,
                    )
                    st.subheader(f"Feedback for {student_id}")
                    st.write(feedback.text)
                except Exception as e:
                    st.error(f"Error evaluating answers: {e}")
        else:
            st.warning("Please fill in your ID and all three answers before submitting.")
