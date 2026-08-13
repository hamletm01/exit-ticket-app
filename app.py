import streamlit as st
from google import genai
import pypdf
import docx
import pandas as pd
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="AI Exit Ticket Portal", page_icon="🎓", layout="wide")

# Custom CSS for Aesthetics & Clean Layout
st.markdown("""
    <style>
    .main-title { font-size: 2rem; font-weight: 700; color: #1E3A8A; margin-bottom: 0.5rem; }
    .stButton>button { border-radius: 0.5rem; font-weight: 600; }
    .sidebar .sidebar-content { background-color: #F8FAFC; }
    </style>
""", unsafe_allow_html=True)

# 1. API Initialization
if "GEMINI_API_KEY" in st.secrets:
    api_key = str(st.secrets["GEMINI_API_KEY"]).strip().strip('"').strip("'")
    client = genai.Client(api_key=api_key)
else:
    st.error("API Key missing in Streamlit Secrets.")
    st.stop()

MODEL_NAME = "gemini-3.6-flash"

# Session State Initialization
if "questions" not in st.session_state:
    st.session_state.questions = None
if "lesson_title" not in st.session_state:
    st.session_state.lesson_title = "General Lesson"
if "student_results" not in st.session_state:
    st.session_state.student_results = []
if "teacher_authenticated" not in st.session_state:
    st.session_state.teacher_authenticated = False

# Helper Function to Extract Text from Uploaded Files
def extract_text(file):
    text = ""
    if file.name.endswith(".pdf"):
        reader = pypdf.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() or ""
    elif file.name.endswith(".docx"):
        doc = docx.Document(file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    elif file.name.endswith(".txt"):
        text = file.read().decode("utf-8")
    return text

# ==========================================
# SIDEBAR: TEACHER LOGIN & NAVIGATION
# ==========================================
with st.sidebar:
    st.title("⚙️ Portal Access")
    
    # Mode Switcher
    app_mode = st.radio("Select View:", ["🎓 Student Portal", "👨‍🏫 Teacher Dashboard"])
    
    if app_mode == "👨‍🏫 Teacher Dashboard":
        st.markdown("---")
        st.subheader("🔒 Teacher Authentication")
        
        # Teacher PIN Check (Default PIN: 1234 or configurable in Secrets)
        TEACHER_PIN = st.secrets.get("TEACHER_PIN", "1234")
        
        pin_input = st.text_input("Enter Teacher PIN:", type="password")
        
        if st.button("Unlock Dashboard"):
            if pin_input == TEACHER_PIN:
                st.session_state.teacher_authenticated = True
                st.success("Authenticated!")
            else:
                st.session_state.teacher_authenticated = False
                st.error("Incorrect PIN")
                
        if st.session_state.teacher_authenticated:
            if st.button("Lock Dashboard 🔒"):
                st.session_state.teacher_authenticated = False
                st.rerun()

# ==========================================
# VIEW 1: STUDENT PORTAL (DEFAULT)
# ==========================================
if app_mode == "🎓 Student Portal":
    st.markdown("<div class='main-title'>🎓 Student Exit Ticket</div>", unsafe_allow_html=True)
    
    if not st.session_state.questions:
        st.info("👋 No active exit ticket published yet. Please wait for your teacher to publish today's lesson ticket!")
    else:
        st.markdown(f"### Current Topic: **{st.session_state.lesson_title}**")
        st.markdown("---")
        
        st.markdown("#### **Today's Questions:**")
        st.info(st.session_state.questions)
        
        with st.form("student_form"):
            student_name = st.text_input("Enter Name / Student ID:")
            a1 = st.text_area("Answer to Question 1:")
            a2 = st.text_area("Answer to Question 2:")
            a3 = st.text_area("Answer to Question 3:")
            
            submitted = st.form_submit_button("Submit Exit Ticket 🚀")
            
            if submitted:
                if student_name and a1 and a2 and a3:
                    with st.spinner("AI Tutor is grading your responses..."):
                        eval_prompt = f"""
                        You are a supportive high school teacher. Evaluate these responses against the lesson questions.
                        Questions: {st.session_state.questions}
                        Student Answers: 1. {a1} | 2. {a2} | 3. {a3}
                        
                        Provide:
                        1. Score out of 3.
                        2. Encouraging feedback on what was correct.
                        3. Specific advice on what to revise.
                        """
                        response = client.models.generate_content(model=MODEL_NAME, contents=eval_prompt)
                        feedback_text = response.text
                        
                        # Store in class records
                        st.session_state.student_results.append({
                            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "Student ID": student_name,
                            "Q1 Answer": a1,
                            "Q2 Answer": a2,
                            "Q3 Answer": a3,
                            "Feedback": feedback_text
                        })
                        
                        st.success("Ticket Submitted Successfully!")
                        st.markdown("### 📝 Your Diagnostic Feedback:")
                        st.write(feedback_text)
                else:
                    st.warning("Please complete all fields before submitting.")

# ==========================================
# VIEW 2: TEACHER DASHBOARD (PROTECTED)
# ==========================================
elif app_mode == "👨‍🏫 Teacher Dashboard":
    st.markdown("<div class='main-title'>👨‍🏫 Teacher Management Studio</div>", unsafe_allow_html=True)
    
    if not st.session_state.teacher_authenticated:
        st.warning("🔒 This area is password protected. Please enter the Teacher PIN in the sidebar to access lesson controls and student analytics.")
    else:
        col_left, col_right = st.columns([1, 1])
        
        with col_left:
            st.markdown("### 1️⃣ Publish Exit Ticket")
            lesson_title = st.text_input("Lesson Title / Topic:", value="Water Cycle & Climate")
            
            uploaded_file = st.file_uploader("Upload Lesson Content (PDF, DOCX, TXT):", type=["pdf", "docx", "txt"])
            raw_notes = st.text_area("...or Paste Lesson Notes/Outline directly:", height=150)
            
            if st.button("Generate & Publish to Class 📢"):
                combined_text = ""
                if uploaded_file:
                    combined_text += extract_text(uploaded_file)
                if raw_notes:
                    combined_text += "\n" + raw_notes
                    
                if combined_text.strip():
                    with st.spinner("Analyzing lesson content & creating ticket..."):
                        gen_prompt = f"""
                        You are an expert Australian High School Curriculum Designer.
                        Based on these lesson materials, create 3 targeted short-answer questions to assess student understanding.
                        
                        Materials:
                        {combined_text[:4000]}
                        """
                        ticket_res = client.models.generate_content(model=MODEL_NAME, contents=gen_prompt)
                        st.session_state.questions = ticket_res.text
                        st.session_state.lesson_title = lesson_title
                        st.success("Exit Ticket Published! Students can now complete it on the Student Portal.")
                else:
                    st.error("Please upload a file or paste text content first.")
                    
        with col_right:
            st.markdown("### 2️⃣ Class Submissions & Analytics")
            if st.session_state.student_results:
                df = pd.DataFrame(st.session_state.student_results)
                st.dataframe(df[["Timestamp", "Student ID", "Feedback"]], use_container_width=True)
                
                # Export CSV
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download Results CSV", data=csv, file_name=f"exit_tickets_{datetime.now().strftime('%Y%m%d')}.csv", mime='text/csv')
                
                # AI Class Insights
                if st.button("🧠 Generate Whole-Class Diagnostic Summary"):
                    with st.spinner("Analyzing class trends..."):
                        class_summary_prompt = f"""
                        Analyze these student submissions for common misconceptions and overall comprehension trends:
                        {df.to_string()}
                        """
                        class_res = client.models.generate_content(model=MODEL_NAME, contents=class_summary_prompt)
                        st.markdown("#### Class Insight Report:")
                        st.write(class_res.text)
            else:
                st.info("No student submissions received for this session yet.")
