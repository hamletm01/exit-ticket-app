import streamlit as st
from google import genai
import pypdf
import docx
import pandas as pd
import json
import re
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

/* Prevent Sidebar Columns from rendering white card frames */
section[data-testid="stSidebar"] div[data-testid="stColumn"] > div {
    background: transparent !important;
    border-radius: 0 !important;
    padding: 0 !important;
    box-shadow: none !important;
    border: none !important;
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

/* iOS Main Content Section Card Styling */
section[data-testid="stMain"] div[data-testid="stColumn"] > div, .ios-card-container {
    background: #FFFFFF !important;
    border-radius: 20px !important;
    padding: 24px !important;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.03), 0 1px 3px rgba(0, 0, 0, 0.02) !important;
    border: 1px solid rgba(0, 0, 0, 0.06) !important;
    overflow: hidden !important;
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
.ios-badge-orange { background: rgba(255, 149, 0, 0.15); color: #FF9500; }

/* Custom Individual Question Box */
.ios-single-qbox {
    background: #F8F9FA;
    border-radius: 16px;
    padding: 18px 20px;
    border-left: 4px solid #007AFF;
    margin-bottom: 12px;
    font-weight: 600;
    font-size: 1rem;
    color: #1C1C1E;
}

/* Feedback Box */
.ios-feedback-card {
    background: #FFFFFF;
    border: 1px solid rgba(52, 199, 89, 0.3);
    border-radius: 20px;
    padding: 28px;
    margin-top: 24px;
    box-shadow: 0 10px 30px rgba(52, 199, 89, 0.1);
}

/* Form Controls & Inputs */
.stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div {
    background-color: #F2F2F7 !important;
    border: 1px solid rgba(0, 0, 0, 0.08) !important;
    border-radius: 12px !important;
    padding: 10px 14px !important;
    font-size: 0.95rem !important;
    color: #1C1C1E !important;
}

.stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
    background-color: #FFFFFF !important;
    border-color: #007AFF !important;
    box-shadow: 0 0 0 4px rgba(0, 122, 255, 0.18) !important;
}

/* iOS Responsive Action Buttons */
.stButton>button, .stDownloadButton>button {
    background: #007AFF !important;
    color: #FFFFFF !important;
    border-radius: 12px !important;
    border: none !important;
    padding: 12px 16px !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 14px rgba(0, 122, 255, 0.28) !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
    white-space: normal !important;
    word-break: break-word !important;
    line-height: 1.3 !important;
    height: auto !important;
    min-height: 44px !important;
}

.stButton>button:hover, .stDownloadButton>button:hover {
    background: #0062D6 !important;
    transform: translateY(-1px) !important;
}

.stButton>button:active, .stDownloadButton>button:active {
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
    st.session_state.questions = "1. Explain the process of evapotranspiration in your own words.\n2. How does the urban heat island effect impact localized weather conditions?\n3. Describe two primary environmental factors that drive atmospheric circulation."
if "lesson_title" not in st.session_state:
    st.session_state.lesson_title = "Water Cycle & Climate Dynamics"
if "student_results" not in st.session_state:
    st.session_state.student_results = []
if "teacher_authenticated" not in st.session_state:
    st.session_state.teacher_authenticated = False
if "ticket_library" not in st.session_state:
    st.session_state.ticket_library = {
        "Water Cycle & Climate Dynamics": "1. Explain the process of evapotranspiration in your own words.\n2. How does the urban heat island effect impact localized weather conditions?\n3. Describe two primary environmental factors that drive atmospheric circulation.",
        "Photosynthesis Basics": "1. What is the overall chemical equation for photosynthesis?\n2. What specific role does chlorophyll play in light absorption?\n3. How do plant stomata regulate gas exchange during high temperatures?"
    }

# Helper: Parse AI raw questions string into list of individual questions
def parse_questions(raw_text):
    if not raw_text:
        return []
    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
    q_list = []
    current_q = ""
    for line in lines:
        if re.match(r'^(\d+[\.\)]|Q\d+:?|Question\s*\d+:?)', line, re.IGNORECASE):
            if current_q:
                q_list.append(current_q)
            current_q = line
        else:
            if current_q:
                current_q += " " + line
            else:
                current_q = line
    if current_q:
        q_list.append(current_q)
    return q_list if len(q_list) > 0 else [raw_text]

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
        
        if not st.session_state.teacher_authenticated:
            if st.button("Unlock Studio 🔓"):
                if pin_input == TEACHER_PIN:
                    st.session_state.teacher_authenticated = True
                    st.rerun()
                else:
                    st.error("Invalid Passcode")
        else:
            if st.button("Lock Studio 🔒"):
                st.session_state.teacher_authenticated = False
                st.rerun()

# ==========================================
# VIEW 1: STUDENT PORTAL (ENHANCED WORKFLOW)
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
        questions_list = parse_questions(st.session_state.questions)
        
        # Student Identity Bar
        col_id, col_stat = st.columns([2, 1])
        with col_id:
            student_name = st.text_input("👤 Your Full Name or Student ID:", placeholder="e.g. Alex Smith")
        with col_stat:
            st.markdown(f"""
            <div style="text-align: right; padding-top: 25px;">
                <span class='ios-badge ios-badge-blue'>{len(questions_list)} Questions Total</span>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("---")
        
        # Form Container
        with st.form("enhanced_student_form", clear_on_submit=False):
            user_answers = []
            
            # Dynamically Render Each Question as an Individual Card
            for idx, q_text in enumerate(questions_list):
                st.markdown(f"""
                <div class="ios-single-qbox">
                    <span style="color: #007AFF; font-weight: 700; margin-right: 6px;">Q{idx+1}:</span> {q_text}
                </div>
                """, unsafe_allow_html=True)
                
                ans = st.text_area(
                    f"Your Response to Q{idx+1}:", 
                    placeholder=f"Write your explanation for Question {idx+1} here...", 
                    height=100, 
                    key=f"ans_{idx}",
                    label_visibility="collapsed"
                )
                user_answers.append(ans)
                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            
            submitted = st.form_submit_button("Submit Exit Ticket 🚀")
            
            if submitted:
                if not student_name.strip():
                    st.error("⚠️ Please enter your Student Name/ID before submitting.")
                elif any(not a.strip() for a in user_answers):
                    st.warning("⚠️ Please answer all questions before submitting your ticket.")
                else:
                    with st.spinner("✨ AI Tutor is evaluating your answers..."):
                        # Format answers for Gemini
                        formatted_qa = "\n".join([f"Q{i+1}: {questions_list[i]}\nAnswer: {user_answers[i]}" for i in range(len(questions_list))])
                        
                        eval_prompt = f"""
                        You are an encouraging high school AI teacher. Evaluate the student's exit ticket answers against the questions.
                        
                        QUESTIONS & ANSWERS:
                        {formatted_qa}
                        
                        INSTRUCTIONS:
                        Provide your feedback with clear sections:
                        1. A score out of {len(questions_list)} (e.g. Score: 3/{len(questions_list)}).
                        2. Key Highlights (What the student understood well).
                        3. Learning Opportunities (Specific advice on what to review or improve).
                        """
                        response = client.models.generate_content(model=MODEL_NAME, contents=eval_prompt)
                        feedback_text = response.text
                        
                        # Store Result
                        res_dict = {
                            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "Student ID": student_name,
                            "Feedback": feedback_text
                        }
                        for i, a in enumerate(user_answers):
                            res_dict[f"Q{i+1} Answer"] = a
                            
                        st.session_state.student_results.append(res_dict)
                        
                        # Render Clean Evaluation View
                        st.markdown(f"""
                        <div class="ios-feedback-card">
                            <span class="ios-badge ios-badge-green">SUBMISSION SUCCESSFUL</span>
                            <h3 style="color: #28CD41; font-weight: 700; margin-top: 6px;">Evaluation Summary for {student_name}</h3>
                            <hr style="border: none; border-top: 1px solid rgba(0,0,0,0.08); margin: 16px 0;">
                            <div style="color: #1C1C1E; font-size: 0.98rem; line-height: 1.6;">
                                {feedback_text.replace('\n', '<br>')}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

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
        
        # --- LEFT COLUMN: GENERATE & TICKET MANAGEMENT ---
        with col_left:
            st.markdown("<span class='ios-badge ios-badge-blue'>CURRICULUM AUTHORING</span>", unsafe_allow_html=True)
            st.markdown("### 1️⃣ Create or Generate Ticket")
            
            lesson_title = st.text_input("Lesson Title / Unit Topic:", value=st.session_state.lesson_title)
            uploaded_file = st.file_uploader("Upload Lesson Content (PDF, DOCX, TXT):", type=["pdf", "docx", "txt"])
            raw_notes = st.text_area("Or Paste Syllabus Notes / Outline:", height=110, placeholder="Paste lesson objectives, key facts, or syllabus points...")
            
            if st.button("Generate & Set Active 📢"):
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
                        Format them strictly as numbered questions (1., 2., 3.).
                        
                        Materials:
                        {combined_text[:4000]}
                        """
                        ticket_res = client.models.generate_content(model=MODEL_NAME, contents=gen_prompt)
                        st.session_state.questions = ticket_res.text
                        st.session_state.lesson_title = lesson_title
                        st.success("Exit Ticket Published! Students can now complete it on the Student Portal.")
                        st.rerun()
                else:
                    st.error("Please upload a file or paste syllabus text first.")

            # --- TICKET LIBRARY (SAVE / LOAD SYSTEM) ---
            st.markdown("---")
            st.markdown("<span class='ios-badge ios-badge-orange'>TICKET LIBRARY & SAVED DRAFTS</span>", unsafe_allow_html=True)
            st.markdown("### 💾 Saved Ticket Manager")
            
            if st.session_state.questions:
                if st.button("💾 Save Current Active Ticket to Library"):
                    st.session_state.ticket_library[st.session_state.lesson_title] = st.session_state.questions
                    st.success(f"Saved '{st.session_state.lesson_title}' to Library!")
            
            if st.session_state.ticket_library:
                selected_ticket = st.selectbox(
                    "Load saved ticket into active session:",
                    options=list(st.session_state.ticket_library.keys())
                )
                
                if st.button("📂 Load Selected Ticket"):
                    st.session_state.lesson_title = selected_ticket
                    st.session_state.questions = st.session_state.ticket_library[selected_ticket]
                    st.success(f"Loaded '{selected_ticket}' into active Student Portal!")
                    st.rerun()

            with st.expander("📤 Export / Import Library File"):
                json_data = json.dumps(st.session_state.ticket_library, indent=2)
                st.download_button(
                    label="📥 Export Library (.json)",
                    data=json_data,
                    file_name="exit_ticket_library.json",
                    mime="application/json"
                )
                
                imported_file = st.file_uploader("Upload Ticket Library (.json):", type=["json"])
                if imported_file:
                    try:
                        imported_data = json.load(imported_file)
                        st.session_state.ticket_library.update(imported_data)
                        st.success("Library updated successfully!")
                    except Exception as e:
                        st.error("Invalid JSON file structure.")

        # --- RIGHT COLUMN: ANALYTICS ---
        with col_right:
            st.markdown("<span class='ios-badge ios-badge-green'>CLASS ANALYTICS ROSTER</span>", unsafe_allow_html=True)
            st.markdown("### 2️⃣ Student Submissions")
            
            if st.session_state.questions:
                st.markdown(f"**Currently Active Ticket:** `{st.session_state.lesson_title}`")
            
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
