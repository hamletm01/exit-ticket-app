import streamlit as st
from google import genai
import pypdf
import docx
import pandas as pd
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="Exit Ticket Studio", 
    page_icon="🎓", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# ==========================================
# APPLE HUMAN INTERFACE DESIGN (HIG) SYSTEM
# ==========================================
st.markdown("""
<style>
/* Import Inter / SF Pro Fallback */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* Global Reset to Apple Typography Stack */
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", "SF Pro", "Helvetica Neue", sans-serif !important;
    background-color: #F2F2F7 !important;
    color: #1C1C1E;
}

.stApp {
    background-color: #F2F2F7 !important;
}

/* Hide Default Streamlit Chrome */
header[data-testid="stHeader"] { background: transparent !important; }
footer { visibility: hidden; }

/* ==========================================
   APPLE IPAD SIDEBAR / CONTROL CENTER
   ========================================== */
section[data-testid="stSidebar"] {
    background-color: rgba(242, 242, 247, 0.75) !important;
    backdrop-filter: blur(40px) saturate(190%) !important;
    -webkit-backdrop-filter: blur(40px) saturate(190%) !important;
    border-right: 1px solid rgba(0, 0, 0, 0.08) !important;
    padding-top: 1rem !important;
}

/* Custom iOS Segmented Control (Radio Button Styling) */
div[data-testid="stRadio"] > div {
    background: rgba(120, 120, 128, 0.12) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    border: none !important;
    gap: 4px !important;
}

div[data-testid="stRadio"] label {
    background: transparent !important;
    border-radius: 8px !important;
    padding: 8px 12px !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
    color: #1C1C1E !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    cursor: pointer !important;
}

/* Highlight Active Segment in iOS Radio Toggle */
div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) {
    background: #FFFFFF !important;
    color: #000000 !important;
    box-shadow: 0 3px 8px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.08) !important;
    font-weight: 600 !important;
}

/* Hide raw radio circle indicators for pure Segmented Control feel */
div[data-testid="stRadio"] input[type="radio"] {
    display: none !important;
}

/* Apple Hero Banners */
.ios-hero-student {
    background: linear-gradient(135deg, #007AFF 0%, #0051A8 100%);
    border-radius: 22px;
    padding: 30px 36px;
    color: #FFFFFF;
    box-shadow: 0 12px 28px rgba(0, 122, 255, 0.25);
    margin-bottom: 24px;
}

.ios-hero-teacher {
    background: linear-gradient(135deg, #5856D6 0%, #AF52DE 100%);
    border-radius: 22px;
    padding: 30px 36px;
    color: #FFFFFF;
    box-shadow: 0 12px 28px rgba(175, 82, 222, 0.25);
    margin-bottom: 24px;
}

.ios-hero-student h1, .ios-hero-teacher h1 {
    font-size: 2.2rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.5px !important;
    color: #FFFFFF !important;
    margin: 0 0 6px 0 !important;
}

.ios-hero-student p, .ios-hero-teacher p {
    font-size: 1.05rem !important;
    opacity: 0.92 !important;
    margin: 0 !important;
    font-weight: 400 !important;
}

/* iOS Section Card Styling */
div[data-testid="stColumn"] > div, .ios-card-container {
    background: #FFFFFF !important;
    border-radius: 20px !important;
    padding: 24px !important;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.03), 0 1px 3px rgba(0, 0, 0, 0.02) !important;
    border: 1px solid rgba(0, 0, 0, 0.06) !important;
}

/* iOS Pill Badges */
.ios-badge {
    display: inline-block;
    padding: 5px 14px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.4px;
    text-transform: uppercase;
    margin-bottom: 14px;
}
.ios-badge-blue { background: rgba(0, 122, 255, 0.12); color: #007AFF; }
.ios-badge-green { background: rgba(52, 199, 89, 0.15); color: #28CD41; }
.ios-badge-purple { background: rgba(175, 82, 222, 0.15); color: #AF52DE; }

/* Custom Question Callout Box */
.ios-question-box {
    background: #F8F9FA;
    border-radius: 16px;
    padding: 22px;
    border-left: 5px solid #007AFF;
    box-shadow: inset 0 0 0 1px rgba(0, 0, 0, 0.04);
    margin-bottom: 24px;
    font-size: 1.05rem;
    line-height: 1.6;
    color: #1C1C1E;
}

/* Feedback Box */
.ios-feedback-card {
    background: rgba(52, 199, 89, 0.08);
    border: 1px solid rgba(52, 199, 89, 0.3);
    border-radius: 18px;
    padding: 24px;
    margin-top: 24px;
}

/* Form Controls & Inputs */
.stTextInput>div>div>input, .stTextArea>div>div>textarea {
    background-color: #F2F2F7 !important;
    border: 1px solid rgba(0, 0, 0, 0.08) !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
    font-size: 0.98rem !important;
    color: #1C1C1E !important;
}

.stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
    background-color: #FFFFFF !important;
    border-color: #007AFF !important;
    box-shadow: 0 0 0 4px rgba(0, 122, 255, 0.18) !important;
}

/* Action Buttons */
.stButton>button {
    background: #007AFF !important;
    color: #FFFFFF !important;
    border-radius: 12px !important;
    border: none !important;
    padding: 12px 24px !important;
    font-size: 0.98rem !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 14px rgba(0, 122, 255, 0.28) !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
}

.stButton>button:hover {
    background: #0062D6 !important;
    transform: translateY(-1px) !important;
}

.stButton>button:active {
    transform: scale(0.98) !important;
}
</style>
""", unsafe_allow_html=True)

# 1. API Initialization
if "GEMINI_API_KEY" in st.secrets:
    api_key = str(st.secrets["GEMINI_API_KEY"]).strip().strip('"').strip("'")
    client = genai.Client(api_key=api_key)
else:
    st.error("⚠️ API Key missing in Streamlit Secrets.")
    st.stop()

MODEL_NAME = "gemini-3.6-flash"

# Session State Initialization
if "questions" not in st.session_state:
    st.session_state.questions = None
if "lesson_title" not in st.session_state:
    st.session_state.lesson_title = "Water Cycle & Climate Dynamics"
if "student_results" not in st.session_state:
    st.session_state.student_results = []
if "teacher_authenticated" not in st.session_state:
    st.session_state.teacher_authenticated = False

# File Text Extraction Helper
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
# SIDEBAR: IPAD CONTROL CENTER
# ==========================================
with st.sidebar:
    st.markdown("""
    <div style="padding: 6px 0 12px 0;">
        <div style="font-size: 0.72rem; font-weight: 700; color: #8E8E93; letter-spacing: 0.8px; text-transform: uppercase;">System Control</div>
        <div style="font-size: 1.35rem; font-weight: 700; color: #1C1C1E; letter-spacing: -0.3px; margin-top: 2px;">Control Center</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='font-size: 0.78rem; font-weight: 600; color: #8E8E93; margin: 12px 0 6px 0; text-transform: uppercase; letter-spacing: 0.5px;'>Portal Mode</div>", unsafe_allow_html=True)
    app_mode = st.radio("Select View:", ["🎓 Student Portal", "👨‍🏫 Teacher Studio"], label_visibility="collapsed")
    
    if app_mode == "👨‍🏫 Teacher Studio":
        st.markdown("<div style='margin-top:20px;'><span class='ios-badge ios-badge-purple'>STUDIO ACCESS</span></div>", unsafe_allow_html=True)
        
        TEACHER_PIN = st.secrets.get("TEACHER_PIN", "1234")
        pin_input = st.text_input("Teacher Passcode:", type="password", placeholder="••••")
        
        col_auth1, col_auth2 = st.columns([1, 1], gap="small")
        with col_auth1:
            if st.button("Unlock"):
                if pin_input == TEACHER_PIN:
                    st.session_state.teacher_authenticated = True
                    st.success("Unlocked")
                else:
                    st.session_state.teacher_authenticated = False
                    st.error("Invalid PIN")
        with col_auth2:
            if st.session_state.teacher_authenticated:
                if st.button("Lock 🔒"):
                    st.session_state.teacher_authenticated = False
                    st.rerun()

# ==========================================
# VIEW 1: STUDENT PORTAL
# ==========================================
if app_mode == "🎓 Student Portal":
    st.markdown(f"""
    <div class="ios-hero-student">
        <h1>🎓 Lesson Exit Ticket</h1>
        <p>Topic: {st.session_state.lesson_title}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.questions:
        st.markdown("""
        <div class="ios-card-container" style="text-align: center; padding: 48px 24px;">
            <div style="font-size: 3rem; margin-bottom: 12px;">⏳</div>
            <h3 style="font-weight: 700; color: #1C1C1E; margin-bottom: 8px;">Waiting for Active Ticket</h3>
            <p style="color: #8E8E93; max-width: 420px; margin: 0 auto;">Your teacher hasn't published an exit ticket for this session yet. Please check back shortly!</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("<span class='ios-badge ios-badge-blue'>REQUIRED COMPREHENSION CHECK</span>", unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="ios-question-box">
            <strong style="color: #007AFF; font-size: 0.88rem; text-transform: uppercase; letter-spacing: 0.5px;">Today's Assessment Questions</strong>
            <div style="margin-top: 10px;">{st.session_state.questions.replace('\n', '<br>')}</div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("student_form", clear_on_submit=False):
            st.markdown("#### **Your Submissions**")
            student_name = st.text_input("Student Name / ID:", placeholder="e.g. Alex Smith")
            a1 = st.text_area("Answer to Question 1:", placeholder="Type your answer...", height=90)
            a2 = st.text_area("Answer to Question 2:", placeholder="Type your answer...", height=90)
            a3 = st.text_area("Answer to Question 3:", placeholder="Type your answer...", height=90)
            
            submitted = st.form_submit_button("Submit Exit Ticket 🚀")
            
            if submitted:
                if student_name and a1 and a2 and a3:
                    with st.spinner("✨ AI Tutor is evaluating your answers..."):
                        eval_prompt = f"""
                        You are a supportive high school teacher. Evaluate these responses against the lesson questions.
                        Questions: {st.session_state.questions}
                        Student Answers: 1. {a1} | 2. {a2} | 3. {a3}
                        
                        Provide:
                        1. Overall Score out of 3 (Format: Score: X/3).
                        2. Encouraging diagnostic feedback on what was correct.
                        3. Clear advice on key concepts to revise before next lesson.
                        """
                        response = client.models.generate_content(model=MODEL_NAME, contents=eval_prompt)
                        feedback_text = response.text
                        
                        st.session_state.student_results.append({
                            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "Student ID": student_name,
                            "Q1 Answer": a1,
                            "Q2 Answer": a2,
                            "Q3 Answer": a3,
                            "Feedback": feedback_text
                        })
                        
                        st.markdown(f"""
                        <div class="ios-feedback-card">
                            <span class="ios-badge ios-badge-green">EVALUATION COMPLETE</span>
                            <h3 style="color: #28CD41; font-weight: 700; margin-top: 6px;">Diagnostic Feedback for {student_name}</h3>
                            <div style="color: #1C1C1E; font-size: 1rem; line-height: 1.6; margin-top: 12px;">
                                {feedback_text.replace('\n', '<br>')}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("Please complete your name and all three answers before submitting.")

# ==========================================
# VIEW 2: TEACHER DASHBOARD
# ==========================================
elif app_mode == "👨‍🏫 Teacher Studio":
    st.markdown("""
    <div class="ios-hero-teacher">
        <h1>👨‍🏫 Teacher Studio</h1>
        <p>Curriculum Design & Live Class Diagnostic Analytics</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.teacher_authenticated:
        st.markdown("""
        <div class="ios-card-container" style="text-align: center; padding: 48px 24px;">
            <div style="font-size: 3rem; margin-bottom: 12px;">🔒</div>
            <h3 style="font-weight: 700; color: #1C1C1E; margin-bottom: 8px;">Dashboard Protected</h3>
            <p style="color: #8E8E93; max-width: 420px; margin: 0 auto;">Please enter the Teacher Passcode in Control Center to unlock lesson authoring and live student records.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        col_left, col_right = st.columns([1, 1], gap="large")
        
        with col_left:
            st.markdown("<span class='ios-badge ios-badge-blue'>CURRICULUM AUTHORING</span>", unsafe_allow_html=True)
            st.markdown("### 1️⃣ Publish Exit Ticket")
            
            lesson_title = st.text_input("Lesson Title / Unit Topic:", value=st.session_state.lesson_title)
            uploaded_file = st.file_uploader("Upload Lesson Content (PDF, DOCX, TXT):", type=["pdf", "docx", "txt"])
            raw_notes = st.text_area("Or Paste Syllabus Notes / Outline:", height=140, placeholder="Paste lesson objectives, key facts, or syllabus points...")
            
            if st.button("Generate & Publish Exit Ticket 📢"):
                combined_text = ""
                if uploaded_file:
                    combined_text += extract_text(uploaded_file)
                if raw_notes:
                    combined_text += "\n" + raw_notes
                    
                if combined_text.strip():
                    with st.spinner("✨ Synthesizing courseware and building questions..."):
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
                    st.error("Please upload a file or paste syllabus text first.")
            
        with col_right:
            st.markdown("<span class='ios-badge ios-badge-green'>CLASS ANALYTICS ROSTER</span>", unsafe_allow_html=True)
            st.markdown("### 2️⃣ Student Submissions")
            
            if st.session_state.student_results:
                df = pd.DataFrame(st.session_state.student_results)
                st.dataframe(df[["Timestamp", "Student ID", "Feedback"]], use_container_width=True, height=220)
                
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Export Results CSV", data=csv, file_name=f"exit_tickets_{datetime.now().strftime('%Y%m%d')}.csv", mime='text/csv')
                
                st.markdown("---")
                if st.button("🧠 Generate Class Diagnostic Trends"):
                    with st.spinner("Analyzing class-wide response data..."):
                        class_summary_prompt = f"""
                        Analyze these student submissions for common misconceptions and overall comprehension trends:
                        {df.to_string()}
                        """
                        class_res = client.models.generate_content(model=MODEL_NAME, contents=class_summary_prompt)
                        st.markdown("<div style='background:#F2F2F7; padding:18px; border-radius:14px; margin-top:14px;'>", unsafe_allow_html=True)
                        st.write(class_res.text)
                        st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("No student responses logged for this active session yet.")
