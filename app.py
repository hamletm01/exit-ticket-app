import streamlit as st
import google.generativeai as genai

# Page Configuration
st.set_page_config(page_title="AI Exit Ticket", page_icon="🎓")

st.title("🎓 Adaptive Lesson Exit Ticket")
st.write("Complete today's exit ticket to check your understanding!")

# 1. Access Gemini API Key from Streamlit Secrets
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("API Key not found. Please configure GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

# Initialize Gemini Model with Fallback Protection
@st.cache_resource
def get_model():
    # Primary model name
    for model_name in ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash-latest"]:
        try:
            m = genai.GenerativeModel(model_name)
            return m
        except Exception:
            continue
    return genai.GenerativeModel("gemini-2.5-flash")

model = get_model()

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
        prompt = f"""
        You are a high school teacher in Australia. Based on the following lesson notes, 
        generate exactly 3 short-answer exit ticket questions to test student comprehension:
        
        Lesson Notes:
        {lesson_notes}
        
        Format your response cleanly with Question 1, Question 2, and Question 3.
        """
        response = model.generate_content(prompt)
        st.session_state.questions = response.text
        st.success("Exit Ticket Created!")

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
                feedback = model.generate_content(eval_prompt)
                st.subheader(f"Feedback for {student_id}")
                st.write(feedback.text)
        else:
            st.warning("Please fill in your ID and all three answers before submitting.")
