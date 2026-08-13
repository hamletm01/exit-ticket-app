import streamlit as st
import google.generativeai as genai

# Page Configuration
st.set_page_config(page_title="AI Exit Ticket", page_icon="🎓")

st.title("🎓 Adaptive Lesson Exit Ticket")
st.write("Complete today's exit ticket to check your understanding!")

# 1. Access & Clean Gemini API Key from Streamlit Secrets
if "GEMINI_API_KEY" in st.secrets:
    # Clean whitespace or extra quotes from copy-pasting
    api_key = str(st.secrets["GEMINI_API_KEY"]).strip().strip('"').strip("'")
    genai.configure(api_key=api_key)
else:
    st.error("API Key not found. Please configure GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

# Auto-discover a working model available to your API key
@st.cache_resource
def get_working_model():
    # List of preferred model identifiers
    candidates = [
        "gemini-2.5-flash",
        "gemini-1.5-flash",
        "gemini-2.0-flash",
        "models/gemini-2.5-flash",
        "models/gemini-1.5-flash"
    ]
    for m_name in candidates:
        try:
            m = genai.GenerativeModel(m_name)
            # Quick ping to verify the model exists for this key
            m.generate_content("Ping", request_options={"timeout": 5})
            return m
        except Exception:
            continue

    # Fallback: Dynamically search all models available on your key
    try:
        for m_info in genai.list_models():
            if "generateContent" in m_info.supported_generation_methods:
                return genai.GenerativeModel(m_info.name)
    except Exception as e:
        st.error(f"API Key connection error: {e}")
        
    return genai.GenerativeModel("gemini-2.5-flash")

# Initialize Model
try:
    model = get_working_model()
except Exception as err:
    st.error(f"Could not initialize model: {err}")
    st.stop()

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
