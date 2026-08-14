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

/* Custom iOS Segmented Control */
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

div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) {
    background: #FFFFFF !important;
    color: #000000 !important;
    box-shadow: 0 3px 8px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.08) !important;
    font-weight: 600 !important;
}

div[data-testid="stRadio"] input[type="radio"] { display: none !important; }

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
.ios-badge-red { background: rgba(255, 59, 48, 0.15); color: #FF3B30; }

/* Custom Question Boxes */
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

.ios-mastery-qbox {
    background: #FFF9F0;
    border-radius: 16px;
    padding: 18px 20px;
    border-left: 4px solid #FF9500;
    margin-bottom: 12px;
    font-weight: 600;
    font-size: 1rem;
    color: #1C1C1E;
}

/* Feedback Card */
.ios-feedback-card {
    background: #FFFFFF;
    border: 1px solid rgba(0, 122, 255, 0.2);
    border-radius: 20px;
    padding: 28px;
    margin-top: 24px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
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

/* Buttons */
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

/* ==========================================
   SAFE & CLEAN SEGMENTED TAB OVERRIDE
   ========================================== */

/* Outer Tab Container */
div[data-baseweb="tab-list"] {
    background-color: rgba(118, 118, 128, 0.12) !important;
    border-radius: 14px !important;
    padding: 4px !important;
    gap: 4px !important;
    border: none !important;
    margin-bottom: 24px !important;
}

/* Base Tab Button */
button[data-baseweb="tab"] {
    background-color: transparent !important;
    border-radius: 10px !important;
    border: none !important;
    padding: 10px 16px !important;
    height: auto !important;
}

/* Force Default Text Color to Dark Grey */
button[data-baseweb="tab"] p, 
button[data-baseweb="tab"] span {
    color: #1C1C1E !important;
    font-weight: 500 !important;
    font-size: 0.95rem !important;
}

/* Active Selected Tab Styling */
button[data-baseweb="tab"][aria-selected="true"] {
    background-color: #FFFFFF !important;
    border-radius: 10px !important;
    box-shadow: 0 3px 8px rgba(0,0,0,0.12) !important;
}

/* Active Selected Text Color Override (Changes Red to Blue) */
button[data-baseweb="tab"][aria-selected="true"] p, 
button[data-baseweb="tab"][aria-selected="true"] span {
    color: #007AFF !important;
    font-weight: 600 !important;
}

/* Hide Red Indicator Bar Cleanly */
div[data-baseweb="tab-highlight"] {
    display: none !important;
}
/* ==========================================
   IPAD NATIVE SEGMENTED CONTROL MENU
   ========================================== */

/* Outer capsule container */
div[data-testid="stRadio"]:has(input[name="teacher_studio_menu"]) > div {
    background-color: rgba(118, 118, 128, 0.16) !important;
    border-radius: 16px !important;
    padding: 6px !important;
    gap: 6px !important;
    display: flex !important;
    flex-direction: row !important;
    width: 100% !important;
}

/* Individual Pill Button (Large Touch Target) */
div[data-testid="stRadio"]:has(input[name="teacher_studio_menu"]) label {
    flex: 1 1 0% !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    padding: 14px 20px !important;
    min-height: 52px !important;        /* Touch-friendly height */
    border-radius: 12px !important;
    background: transparent !important;
    color: #1C1C1E !important;
    font-weight: 500 !important;
    font-size: 1rem !important;
    cursor: pointer !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    border: none !important;
    margin: 0 !important;
    text-align: center !important;
}

/* Active Selected Pill */
div[data-testid="stRadio"]:has(input[name="teacher_studio_menu"]) label:has(input:checked) {
    background-color: #FFFFFF !important;
    color: #007AFF !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12), 0 1px 3px rgba(0, 0, 0, 0.08) !important;
}

/* Hide raw radio circles */
div[data-testid="stRadio"]:has(input[name="teacher_studio_menu"]) input[type="radio"] {
    display: none !important;
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

if "student_misconceptions" not in st.session_state:
    st.session_state.student_misconceptions = {}

# Helper Functions
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
        student_name = st.text_input("👤 Enter Your Name or Student ID to begin:", key="student_id_input", placeholder="e.g. Alex Smith")
        clean_name = student_name.strip().title() if student_name else ""
        
        if clean_name:
            base_questions = parse_questions(st.session_state.questions)
            mastery_question = None
            
            unresolved_gaps = [
                gap for gap in st.session_state.student_misconceptions.get(clean_name, [])
                if not gap.get("resolved", False)
            ]
            
            if unresolved_gaps:
                last_gap = unresolved_gaps[-1]
                st.markdown("<span class='ios-badge ios-badge-orange'>🔄 MASTERY LOOP ACTIVE</span>", unsafe_allow_html=True)
                
                with st.spinner("🔄 Building your personalized revision question from last lesson..."):
                    mastery_prompt = f"""
                    A student named {clean_name} made an error in a previous lesson on topic '{last_gap['lesson']}'.
                    Their identified misconception/error was: "{last_gap['misconception']}".
                    
                    Create 1 short review question that re-tests this specific concept in a clear, supportive way to see if they've mastered it now.
                    Return ONLY the question text.
                    """
                    m_res = client.models.generate_content(model=MODEL_NAME, contents=mastery_prompt)
                    mastery_question = m_res.text.strip()
            
            total_count = len(base_questions) + (1 if mastery_question else 0)
            
            st.markdown(f"""
            <div style="text-align: right; margin-bottom: 10px;">
                <span class='ios-badge ios-badge-blue'>{total_count} Questions Assigned</span>
            </div>
            """, unsafe_allow_html=True)
            
            with st.form("mastery_student_form", clear_on_submit=False):
                user_answers = []
                all_questions = []
                
                if mastery_question:
                    st.markdown(f"""
                    <div class="ios-mastery-qbox">
                        <span style="color: #FF9500; font-weight: 700;">🔄 Mastery Question (Revision):</span> {mastery_question}
                    </div>
                    """, unsafe_allow_html=True)
                    m_ans = st.text_area("Your Revision Response:", placeholder="Answer your revision question here...", height=95, key="m_ans", label_visibility="collapsed")
                    user_answers.append(m_ans)
                    all_questions.append(f"[Mastery Question] {mastery_question}")
                    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
                
                for idx, q_text in enumerate(base_questions):
                    st.markdown(f"""
                    <div class="ios-single-qbox">
                        <span style="color: #007AFF; font-weight: 700; margin-right: 6px;">Q{idx+1}:</span> {q_text}
                    </div>
                    """, unsafe_allow_html=True)
                    ans = st.text_area(f"Your Response to Q{idx+1}:", placeholder=f"Write your response to Question {idx+1}...", height=95, key=f"ans_{idx}", label_visibility="collapsed")
                    user_answers.append(ans)
                    all_questions.append(q_text)
                    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                
                submitted = st.form_submit_button("Submit Exit Ticket 🚀")
                
                if submitted:
                    if any(not a.strip() for a in user_answers):
                        st.warning("⚠️ Please provide answers to all questions before submitting.")
                    else:
                        with st.spinner("✨ Analyzing responses and crafting your targeted feedback..."):
                            qa_payload = ""
                            for q, a in zip(all_questions, user_answers):
                                qa_payload += f"Question: {q}\nStudent Answer: {a}\n---\n"
                            
                            eval_prompt = f"""
                            You are a supportive, high-efficiency high school AI tutor.
                            Evaluate this student's ({clean_name}) exit ticket submission.
                            
                            Topic: {st.session_state.lesson_title}
                            Submission Data:
                            {qa_payload}
                            
                            Respond in the following structured JSON format:
                            {{
                                "score": "X/{len(all_questions)}",
                                "correct_aspects": "Encouraging summary of what they answered correctly.",
                                "incorrect_aspects": "Clear breakdown of what was incorrect or missing in their answers.",
                                "revision_topics": ["Specific concept 1 to review", "Specific concept 2 to review"],
                                "teacher_clarification_question": "A single specific, well-formulated question the student should ask their teacher next lesson to resolve their confusion.",
                                "has_misconception": true/false,
                                "misconception_summary": "Short 1-sentence summary of their key error/misconception if any, or null if all correct."
                            }}
                            """
                            
                            response = client.models.generate_content(
                                model=MODEL_NAME, 
                                contents=eval_prompt,
                                config={"response_mime_type": "application/json"}
                            )
                            
                            try:
                                result_json = json.loads(response.text)
                            except:
                                result_json = {
                                    "score": f"?/{len(all_questions)}",
                                    "correct_aspects": "Great effort completing the exit ticket!",
                                    "incorrect_aspects": "Please review the lesson notes.",
                                    "revision_topics": ["Core lesson concepts"],
                                    "teacher_clarification_question": "Can you explain the main concept from today's lesson again?",
                                    "has_misconception": False,
                                    "misconception_summary": None
                                }
                            
                            if clean_name not in st.session_state.student_misconceptions:
                                st.session_state.student_misconceptions[clean_name] = []
                                
                            if mastery_question and not result_json.get("has_misconception", False):
                                for gap in st.session_state.student_misconceptions[clean_name]:
                                    gap["resolved"] = True
                            
                            if result_json.get("has_misconception") and result_json.get("misconception_summary"):
                                st.session_state.student_misconceptions[clean_name].append({
                                    "lesson": st.session_state.lesson_title,
                                    "misconception": result_json["misconception_summary"],
                                    "resolved": False
                                })
                            
                            res_entry = {
                                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                "Student ID": clean_name,
                                "Score": result_json.get("score"),
                                "Misconception Summary": result_json.get("misconception_summary", "None"),
                                "Full Feedback": response.text
                            }
                            st.session_state.student_results.append(res_entry)
                            
                            st.markdown(f"""
                            <div class="ios-feedback-card">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span class="ios-badge ios-badge-green">EVALUATION COMPLETE</span>
                                    <span class="ios-badge ios-badge-blue">SCORE: {result_json.get('score')}</span>
                                </div>
                                
                                <h3 style="color: #1C1C1E; font-weight: 700; margin-top: 8px;">Diagnostic Feedback for {clean_name}</h3>
                                <hr style="border: none; border-top: 1px solid rgba(0,0,0,0.08); margin: 16px 0;">
                                
                                <p><strong style="color: #28CD41;">✅ What You Understood Well:</strong><br>{result_json.get('correct_aspects')}</p>
                                
                                <p><strong style="color: #FF3B30;">🔍 Areas needing Attention:</strong><br>{result_json.get('incorrect_aspects')}</p>
                                
                                <div style="background: #F2F2F7; padding: 16px; border-radius: 14px; margin: 16px 0;">
                                    <strong style="color: #007AFF;">📖 What to Revise Before Next Lesson:</strong>
                                    <ul style="margin: 8px 0 0 18px; padding: 0;">
                                        {"".join([f"<li>{t}</li>" for t in result_json.get('revision_topics', [])])}
                                    </ul>
                                </div>
                                
                                <div style="background: rgba(255, 149, 0, 0.12); border-left: 4px solid #FF9500; padding: 16px; border-radius: 12px; margin-top: 16px;">
                                    <strong style="color: #FF9500;">🙋 Question to Ask Your Teacher Next Lesson:</strong>
                                    <p style="margin: 6px 0 0 0; font-weight: 600; color: #1C1C1E;">"{result_json.get('teacher_clarification_question')}"</p>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

# ==========================================
# VIEW 2: TEACHER DASHBOARD & ANALYTICS
# ==========================================
elif app_mode == "👨‍🏫 Teacher Studio":
    st.markdown("""
    <div class="ios-hero-teacher">
        <h1>👨‍🏫 Teacher Studio & Analytics</h1>
        <p>Curriculum Design, Live Class Diagnostic Analytics & Targeted Intervention</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.teacher_authenticated:
        st.markdown("""
        <div class="ios-card-container" style="text-align: center; padding: 48px 24px;">
            <div style="font-size: 3rem; margin-bottom: 12px;">🔒</div>
            <h3 style="font-weight: 700; color: #1C1C1E; margin-bottom: 8px;">Dashboard Protected</h3>
            <p style="color: #8E8E93; max-width: 420px; margin: 0 auto;">Please enter the Teacher Passcode in the Control Center to unlock lesson authoring and live student analytics.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
       selected_tab = st.radio(
            "Teacher Studio Navigation",
            ["📝 Ticket Authoring", "📊 Class Analytics & AI Insights", "🔄 Mastery Loop Registry"],
            key="teacher_studio_menu",
            horizontal=True,
            label_visibility="collapsed"
        )

        # ------------------------------------------
        # TAB 1: CURRICULUM AUTHORING
        # ------------------------------------------
        if selected_tab == "📝 Ticket Authoring":
            col_left, col_right = st.columns([1, 1], gap="large")
            with col_left:
                st.markdown("<span class='ios-badge ios-badge-blue'>CURRICULUM AUTHORING</span>", unsafe_allow_html=True)
                st.markdown("### Create or Generate Ticket")
                
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
                            You are an expert High School Curriculum Designer.
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

            with col_right:
                st.markdown("<span class='ios-badge ios-badge-orange'>TICKET LIBRARY</span>", unsafe_allow_html=True)
                st.markdown("### 💾 Saved Ticket Manager")
                
                if st.session_state.questions:
                    if st.button("💾 Save Active Ticket to Library"):
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

        # ------------------------------------------
        # TAB 2: CLASS ANALYTICS & AI INSIGHTS
        # ------------------------------------------
        elif selected_tab == "📊 Class Analytics & AI Insights":
            st.markdown("<span class='ios-badge ios-badge-green'>REAL-TIME CLASS DIAGNOSTICS</span>", unsafe_allow_html=True)
            
            if not st.session_state.student_results:
                st.info("💡 No student submissions recorded yet. Once students submit their exit tickets, diagnostic data will populate here in real time.")
            else:
                df_results = pd.DataFrame(st.session_state.student_results)
                
                # Metrics Bar
                m1, m2, m3, m4 = st.columns(4)
                total_submissions = len(df_results)
                misconception_count = sum(1 for r in st.session_state.student_results if r.get("Misconception Summary") != "None")
                
                m1.metric("Total Submissions", total_submissions)
                m2.metric("Active Misconceptions", misconception_count)
                m3.metric("Current Unit", st.session_state.lesson_title[:18] + "...")
                m4.metric("System Health", "Optimal 🟢")
                
                st.markdown("---")
                
                # Class Synthesis Generator
                st.markdown("### 🤖 Class-Wide AI Synthesis")
                if st.button("Generate Class Analysis & Intervention Plan 💡"):
                    with st.spinner("Analyzing whole-class trends..."):
                        synthesis_prompt = f"""
                        You are an expert instructional coach. Review these exit ticket results for the lesson "{st.session_state.lesson_title}":
                        
                        Data:
                        {json.dumps(st.session_state.student_results)}
                        
                        Provide a clear synthesis:
                        1. Major overall trends across all students.
                        2. Key recurring misconceptions identified.
                        3. Suggested mini-lesson or warm-up activity for the start of next class.
                        """
                        synth_res = client.models.generate_content(model=MODEL_NAME, contents=synthesis_prompt)
                        st.write(synth_res.text)

                st.markdown("### 📋 Student Submissions Table")
                st.dataframe(df_results[["Timestamp", "Student ID", "Score", "Misconception Summary"]], use_container_width=True)

        # ------------------------------------------
        # TAB 3: MASTERY LOOP REGISTRY
        # ------------------------------------------
        elif selected_tab == "🔄 Mastery Loop Registry":
            st.markdown("<span class='ios-badge ios-badge-purple'>MASTERY LOOP REGISTRY</span>", unsafe_allow_html=True)
            st.markdown("### Active & Resolved Student Misconceptions")
            
            if not st.session_state.student_misconceptions:
                st.info("No misconceptions tracked yet.")
            else:
                for student, gaps in st.session_state.student_misconceptions.items():
                    with st.expander(f"👤 {student} ({len(gaps)} total records)"):
                        for gap in gaps:
                            status = "✅ Resolved" if gap.get("resolved") else "🚨 Active Gap"
                            st.write(f"- **[{status}]** `{gap['lesson']}`: {gap['misconception']}")
