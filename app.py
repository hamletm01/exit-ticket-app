import streamlit as st
from google import genai
from google.genai import types
import pypdf
import docx
import pandas as pd
import json
import re
import os
import requests
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="Exit Ticket Studio", 
    page_icon="🎓", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# ==========================================
# SHARED PERSISTENT DATABASE ENGINE (JSONBin API)
# ==========================================
JSONBIN_API_KEY = st.secrets.get("JSONBIN_API_KEY", "")
JSONBIN_BIN_ID = st.secrets.get("JSONBIN_BIN_ID", "")

DEFAULT_DB = {
    "courses": ["Earth Science", "Environmental Studies", "AP Biology", "Physics 101"],
    "course_periods": {
        "Earth Science": ["Period 1 - Oct 12", "Period 2 - Oct 12", "Period 1 - Oct 14"],
        "Environmental Studies": ["Period 3 - Oct 12", "Period 3 - Oct 14"],
        "AP Biology": ["Period 4 - Oct 11"],
        "Physics 101": ["Period 6 - Oct 11"]
    },
    "session_tickets": {},
    "student_results": {},
    "student_misconceptions": {},
    "ticket_library": {}
}

def load_db():
    if not JSONBIN_API_KEY or not JSONBIN_BIN_ID:
        return DEFAULT_DB
    
    headers = {"X-Master-Key": JSONBIN_API_KEY}
    url = f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}/latest"
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()["record"]
        return DEFAULT_DB
    except Exception:
        return DEFAULT_DB

def save_db(data):
    if not JSONBIN_API_KEY or not JSONBIN_BIN_ID:
        return
        
    headers = {
        "Content-Type": "application/json",
        "X-Master-Key": JSONBIN_API_KEY
    }
    url = f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}"
    
    try:
        requests.put(url, headers=headers, json=data, timeout=5)
    except Exception as e:
        st.error(f"Error saving data to cloud database: {e}")

# Load global database into memory for this request
db = load_db()

# Sync DB list defaults if empty
if not db.get("courses"):
    db["courses"] = DEFAULT_DB["courses"]
if not db.get("course_periods"):
    db["course_periods"] = DEFAULT_DB["course_periods"]

# Initialize Active Selection in local session
if "active_course" not in st.session_state or st.session_state.active_course not in db["courses"]:
    st.session_state.active_course = db["courses"][0]

available_p = db["course_periods"].get(st.session_state.active_course, ["Period 1"])
if "active_period" not in st.session_state or st.session_state.active_period not in available_p:
    st.session_state.active_period = available_p[0]

if "teacher_authenticated" not in st.session_state:
    st.session_state.teacher_authenticated = False

# ==========================================
# APPLE HUMAN INTERFACE DESIGN (HIG) SYSTEM
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", "SF Pro", "Helvetica Neue", sans-serif !important;
    background-color: #F2F2F7 !important;
    color: #1C1C1E;
}

.stApp { background-color: #F2F2F7 !important; }
header[data-testid="stHeader"] { background: transparent !important; }
footer { visibility: hidden; }

/* Uniform Vertical Spacing Helper */
.ios-spacer {
    height: 16px;
    width: 100%;
}

section[data-testid="stSidebar"] {
    background-color: rgba(242, 242, 247, 0.75) !important;
    backdrop-filter: blur(40px) saturate(190%) !important;
    -webkit-backdrop-filter: blur(40px) saturate(190%) !important;
    border-right: 1px solid rgba(0, 0, 0, 0.08) !important;
    padding-top: 1rem !important;
}

/* Sidebar Radio Buttons */
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

/* Hero Containers */
.ios-hero-student {
    background: linear-gradient(135deg, #007AFF 0%, #0051A8 100%);
    border-radius: 22px;
    padding: 24px 30px;
    color: #FFFFFF;
    box-shadow: 0 12px 28px rgba(0, 122, 255, 0.25);
    margin-bottom: 16px;
}

.ios-hero-teacher {
    background: linear-gradient(135deg, #5856D6 0%, #AF52DE 100%);
    border-radius: 22px;
    padding: 24px 30px;
    color: #FFFFFF;
    box-shadow: 0 12px 28px rgba(175, 82, 222, 0.25);
    margin-bottom: 16px;
}

.ios-hero-student h1, .ios-hero-teacher h1 {
    font-size: 2.1rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.5px !important;
    color: #FFFFFF !important;
    margin: 0 0 4px 0 !important;
}

.ios-hero-student p, .ios-hero-teacher p {
    font-size: 1rem !important;
    opacity: 0.92 !important;
    margin: 0 !important;
    font-weight: 400 !important;
}

section[data-testid="stMain"] div[data-testid="stColumn"] > div, .ios-card-container {
    background: #FFFFFF !important;
    border-radius: 20px !important;
    padding: 24px !important;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.03), 0 1px 3px rgba(0, 0, 0, 0.02) !important;
    border: 1px solid rgba(0, 0, 0, 0.06) !important;
    overflow: hidden !important;
}

.ios-badge {
    display: inline-block;
    padding: 5px 14px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.4px;
    text-transform: uppercase;
    margin-bottom: 12px;
}
.ios-badge-blue { background: rgba(0, 122, 255, 0.12); color: #007AFF; }
.ios-badge-green { background: rgba(52, 199, 89, 0.15); color: #28CD41; }
.ios-badge-purple { background: rgba(175, 82, 222, 0.15); color: #AF52DE; }
.ios-badge-orange { background: rgba(255, 149, 0, 0.15); color: #FF9500; }

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

.ios-feedback-card {
    background: #FFFFFF;
    border: 1px solid rgba(0, 122, 255, 0.2);
    border-radius: 20px;
    padding: 28px;
    margin-top: 24px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
}

.stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div {
    background-color: #F2F2F7 !important;
    border: 1px solid rgba(0, 0, 0, 0.08) !important;
    border-radius: 12px !important;
    padding: 10px 14px !important;
    font-size: 0.95rem !important;
    color: #1C1C1E !important;
}

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
}

/* CENTERED TAB CONTAINER OVERRIDES */
div[data-testid="stTabs"] {
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    width: 100% !important;
}

div[data-baseweb="tab-list"] {
    background-color: rgba(118, 118, 128, 0.12) !important;
    border-radius: 14px !important;
    padding: 4px !important;
    gap: 4px !important;
    width: 100% !important;
    max-width: 900px !important;
    display: flex !important;
    justify-content: center !important;
    margin: 0 auto 20px auto !important;
}

div[data-baseweb="tab-list"] button {
    flex: 1 1 0px !important;
    border-radius: 10px !important;
    padding: 10px 12px !important;
    font-weight: 500 !important;
    font-size: 0.92rem !important;
    color: #1C1C1E !important;
    background-color: transparent !important;
    border: none !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    text-align: center !important;
}

div[data-baseweb="tab-list"] button[aria-selected="true"] {
    background-color: #FFFFFF !important;
    color: #5856D6 !important;
    font-weight: 600 !important;
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08), 0 1px 2px rgba(0, 0, 0, 0.04) !important;
}

div[data-baseweb="tab-panel"] {
    width: 100% !important;
}

div[data-baseweb="tab-highlight-title"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# API Initialization
if "GEMINI_API_KEY" in st.secrets:
    api_key = str(st.secrets["GEMINI_API_KEY"]).strip().strip('"').strip("'")
    client = genai.Client(api_key=api_key)
else:
    st.error("⚠️ API Key missing in Streamlit Secrets.")
    st.stop()

MODEL_NAME = "gemini-2.5-flash"

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

def extract_text_fallback(file):
    text = ""
    if file.name.endswith(".docx"):
        doc = docx.Document(file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    elif file.name.endswith(".txt"):
        text = file.read().decode("utf-8")
    return text

# ==========================================
# SIDEBAR: SYSTEM & ACCESS CONTROL ONLY
# ==========================================
with st.sidebar:
    st.markdown("""
    <div style="padding: 6px 0 12px 0;">
        <div style="font-size: 0.72rem; font-weight: 700; color: #8E8E93; letter-spacing: 0.8px; text-transform: uppercase;">System Control</div>
        <div style="font-size: 1.35rem; font-weight: 700; color: #1C1C1E; letter-spacing: -0.3px; margin-top: 2px;">Control Center</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='font-size: 0.78rem; font-weight: 600; color: #8E8E93; margin: 12px 0 6px 0; text-transform: uppercase;'>Portal Mode</div>", unsafe_allow_html=True)
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

# Helper function to render Course/Period dropdowns
def render_scope_selectors():
    c_sel_1, c_sel_2 = st.columns(2, gap="large")
    with c_sel_1:
        course_list = db.get("courses", [])
        selected_course = st.selectbox(
            "📚 Active Course",
            options=course_list,
            index=course_list.index(st.session_state.active_course) if st.session_state.active_course in course_list else 0
        )
        st.session_state.active_course = selected_course

    with c_sel_2:
        periods_list = db.get("course_periods", {}).get(selected_course, ["Period 1"])
        current_p_idx = periods_list.index(st.session_state.active_period) if st.session_state.active_period in periods_list else 0
        selected_period = st.selectbox(
            "📅 Active Period / Session",
            options=periods_list,
            index=current_p_idx
        )
        st.session_state.active_period = selected_period

def get_current_ticket():
    session_key = f"{st.session_state.active_course}::{st.session_state.active_period}"
    return session_key, db.get("session_tickets", {}).get(session_key, {"title": "No Published Ticket", "questions": ""})

# ==========================================
# VIEW 1: STUDENT PORTAL
# ==========================================
if app_mode == "🎓 Student Portal":
    render_scope_selectors()
    session_key, curr_ticket = get_current_ticket()

    st.markdown(f"""
    <div class="ios-hero-student">
        <h1>🎓 Lesson Exit Ticket</h1>
        <p>Topic: <strong>{curr_ticket['title']}</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='ios-spacer'></div>", unsafe_allow_html=True)
    
    if not curr_ticket['questions']:
        st.markdown("""
        <div class="ios-card-container" style="text-align: center; padding: 48px 24px;">
            <div style="font-size: 3rem; margin-bottom: 12px;">⏳</div>
            <h3 style="font-weight: 700; color: #1C1C1E; margin-bottom: 8px;">Waiting for Active Ticket</h3>
            <p style="color: #8E8E93; max-width: 420px; margin: 0 auto;">Your teacher hasn't published an exit ticket for this period yet. Please select another Course or Period from the options above!</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        student_name = st.text_input("👤 Enter Your Name or Student ID to begin:", key="student_id_input", placeholder="e.g. Alex Smith")
        clean_name = student_name.strip().title() if student_name else ""
        
        if clean_name:
            base_questions = parse_questions(curr_ticket['questions'])
            mastery_question = None
            
            class_gaps = db.get("student_misconceptions", {}).get(session_key, {}).get(clean_name, [])
            unresolved_gaps = [gap for gap in class_gaps if not gap.get("resolved", False)]
            
            if unresolved_gaps:
                last_gap = unresolved_gaps[-1]
                st.markdown("<span class='ios-badge ios-badge-orange'>🔄 MASTERY LOOP ACTIVE</span>", unsafe_allow_html=True)
                
                with st.spinner("🔄 Building your personalized revision question from last lesson..."):
                    mastery_prompt = f"""
                    A student named {clean_name} made an error in a previous lesson on topic '{last_gap['lesson']}'.
                    Their identified misconception/error was: "{last_gap['misconception']}".
                    
                    Create 1 short review question that re-tests this specific concept in a clear, supportive way to see if they've mastered it now.
                    Phrase it as a direct classroom question without referring to texts or documents.
                    Return ONLY the question text.
                    """
                    m_res = client.models.generate_content(
                        model=MODEL_NAME, 
                        contents=mastery_prompt,
                        config=types.GenerateContentConfig(temperature=0.0)
                    )
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
                            
                            Course: {st.session_state.active_course}
                            Period: {st.session_state.active_period}
                            Topic: {curr_ticket['title']}
                            Submission Data:
                            {qa_payload}
                            
                            Respond in the following structured JSON format:
                            {{
                                "score": "X/{len(all_questions)}",
                                "correct_aspects": "Encouraging summary of what they answered correctly.",
                                "incorrect_aspects": "Clear breakdown of what was incorrect or missing in their answers.",
                                "revision_topics": ["Specific concept 1 to review", "Specific concept 2 to review"],
                                "teacher_clarification_question": "A single specific question the student should ask their teacher next lesson.",
                                "has_misconception": true/false,
                                "misconception_summary": "Short 1-sentence summary of key error if any, or null if all correct."
                            }}
                            """
                            
                            response = client.models.generate_content(
                                model=MODEL_NAME, 
                                contents=eval_prompt,
                                config=types.GenerateContentConfig(
                                    response_mime_type="application/json",
                                    temperature=0.0
                                )
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
                            
                            fresh_db = load_db()
                            
                            if session_key not in fresh_db["student_misconceptions"]:
                                fresh_db["student_misconceptions"][session_key] = {}
                            if clean_name not in fresh_db["student_misconceptions"][session_key]:
                                fresh_db["student_misconceptions"][session_key][clean_name] = []
                                
                            if mastery_question and not result_json.get("has_misconception", False):
                                for gap in fresh_db["student_misconceptions"][session_key][clean_name]:
                                    gap["resolved"] = True
                            
                            if result_json.get("has_misconception") and result_json.get("misconception_summary"):
                                fresh_db["student_misconceptions"][session_key][clean_name].append({
                                    "lesson": curr_ticket['title'],
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
                            
                            if session_key not in fresh_db["student_results"]:
                                fresh_db["student_results"][session_key] = []
                            fresh_db["student_results"][session_key].append(res_entry)
                            
                            save_db(fresh_db)
                            
                            revision_items = "".join([f"<li>{t}</li>" for t in result_json.get('revision_topics', [])])

                            st.markdown(
f"""<div class="ios-feedback-card">
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
{revision_items}
</ul>
</div>

<div style="background: rgba(255, 149, 0, 0.12); border-left: 4px solid #FF9500; padding: 16px; border-radius: 12px; margin-top: 16px;">
<strong style="color: #FF9500;">🙋 Question to Ask Your Teacher Next Lesson:</strong>
<p style="margin: 6px 0 0 0; font-weight: 600; color: #1C1C1E;">"{result_json.get('teacher_clarification_question')}"</p>
</div>
</div>""", 
unsafe_allow_html=True
)

# ==========================================
# VIEW 2: TEACHER DASHBOARD & ANALYTICS
# ==========================================
elif app_mode == "👨‍🏫 Teacher Studio":
    st.markdown("""
    <div class="ios-hero-teacher">
        <h1>👨‍🏫 Teacher Studio & Analytics</h1>
        <p>Curriculum Design & Live Learning Diagnostics</p>
    </div>
    """, unsafe_allow_html=True)
    
    render_scope_selectors()
    session_key, curr_ticket = get_current_ticket()
    
    st.markdown("<div class='ios-spacer'></div>", unsafe_allow_html=True)
    
    if not st.session_state.teacher_authenticated:
        st.markdown("""
        <div class="ios-card-container" style="text-align: center; padding: 48px 24px;">
            <div style="font-size: 3rem; margin-bottom: 12px;">🔒</div>
            <h3 style="font-weight: 700; color: #1C1C1E; margin-bottom: 8px;">Dashboard Protected</h3>
            <p style="color: #8E8E93; max-width: 420px; margin: 0 auto;">Please enter the Teacher Passcode in the Control Center (left sidebar) to unlock lesson authoring and live student analytics.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        tab1, tab2, tab3 = st.tabs(["📝 Ticket Authoring", "📊 Class Analytics & AI Insights", "🔄 Mastery Loop Registry"])

        # TAB 1: AUTHORING
        with tab1:
            st.markdown("<div class='ios-spacer'></div>", unsafe_allow_html=True)
            c1, c2 = st.columns(2, gap="large")
            with c1:
                with st.expander("➕ Add New Course / Class"):
                    new_course_input = st.text_input("New Course Name:", placeholder="e.g. AP Chemistry")
                    if st.button("Add Course 📚"):
                        if new_course_input:
                            fresh_db = load_db()
                            if new_course_input not in fresh_db["courses"]:
                                fresh_db["courses"].append(new_course_input)
                                fresh_db["course_periods"][new_course_input] = ["Period 1"]
                                save_db(fresh_db)
                                st.session_state.active_course = new_course_input
                                st.session_state.active_period = "Period 1"
                                st.success(f"Course '{new_course_input}' created & saved globally!")
                                st.rerun()

            with c2:
                with st.expander(f"➕ Create Session/Period for {st.session_state.active_course}"):
                    p_num = st.selectbox("Period Identifier:", ["Period 1", "Period 2", "Period 3", "Period 4", "Period 5", "Period 6"])
                    p_date = st.date_input("Session Date:")
                    new_period_key = f"{p_num} - {p_date.strftime('%b %d')}"
                    
                    if st.button("Initialize New Session 🚀"):
                        fresh_db = load_db()
                        active_crs = st.session_state.active_course
                        if active_crs not in fresh_db["course_periods"]:
                            fresh_db["course_periods"][active_crs] = []
                        if new_period_key not in fresh_db["course_periods"][active_crs]:
                            fresh_db["course_periods"][active_crs].append(new_period_key)
                            save_db(fresh_db)
                            st.session_state.active_period = new_period_key
                            st.success(f"Created & saved session: {new_period_key}")
                            st.rerun()

            st.markdown("<div class='ios-spacer'></div>", unsafe_allow_html=True)

            col_left, col_right = st.columns([1, 1], gap="large")
            with col_left:
                st.markdown("<span class='ios-badge ios-badge-blue'>CURRICULUM AUTHORING</span>", unsafe_allow_html=True)
                st.markdown(f"### Create Ticket for {st.session_state.active_period}")
                
                lesson_title = st.text_input("Lesson Title / Unit Topic:", value=curr_ticket.get('title', ''))
                uploaded_file = st.file_uploader("Upload Lesson Content (PDF, DOCX, TXT):", type=["pdf", "docx", "txt"])
                raw_notes = st.text_area("Or Paste Syllabus Notes / Outline:", height=110, placeholder="Paste lesson objectives, key facts, or syllabus points...")
                
                if st.button("Generate & Publish Ticket 📢"):
                    contents_payload = []
                    
                    if uploaded_file or raw_notes.strip():
                        with st.spinner("✨ Processing document with Gemini vision & authoring ticket..."):
                            # 1. Direct Multimodal Attachment (PDFs passed directly as byte streams)
                            if uploaded_file is not None:
                                file_bytes = uploaded_file.getvalue()
                                mime_type = uploaded_file.type
                                
                                # Infer MIME type fallback if missing
                                if not mime_type:
                                    if uploaded_file.name.endswith(".pdf"):
                                        mime_type = "application/pdf"
                                    elif uploaded_file.name.endswith(".txt"):
                                        mime_type = "text/plain"
                                    else:
                                        mime_type = "application/octet-stream"

                                if mime_type == "application/pdf":
                                    contents_payload.append(
                                        types.Part.from_bytes(
                                            data=file_bytes,
                                            mime_type="application/pdf"
                                        )
                                    )
                                else:
                                    # Fallback text extraction for docx/txt
                                    txt = extract_text_fallback(uploaded_file)
                                    if txt:
                                        contents_payload.append(f"Document Text:\n{txt}")

                            # 2. Add teacher notes if provided
                            if raw_notes.strip():
                                contents_payload.append(f"Additional Lesson Notes:\n{raw_notes.strip()}")

                            # 3. Add explicit prompt enforcing focus on primary educational content
                            gen_prompt = """
                            You are a classroom teacher creating an exit ticket quiz for your students based ONLY on the primary educational content in the attached document/notes.

                            STRICT RULES FOR QUESTION GENERATION:
                            1. IGNORE METADATA & FORM ARTIFACTS: Completely ignore document headers, page numbers, form fields, sequence tags, PINs, or internal PDF structures.
                            2. NO REPETITION OR OVERLAP: Each of the 3 questions MUST test a COMPLETELY DIFFERENT concept, definition, detail, or process from the lesson content body.
                            3. QUESTION DIVERSITY:
                               - Question 1: Ask about the main definition or primary concept presented.
                               - Question 2: Ask about a specific mechanism, process, stage, or relationship described.
                               - Question 3: Ask about a specific detail, key term, diagram label, or real-world application mentioned.
                            4. Direct Classroom Phrasing: Phrase questions naturally as direct classroom checks (e.g., "What is...", "How does...", "Describe how...").
                            5. NO Meta-References: NEVER refer to "the attached document", "the text", or "source file".

                            FORMAT OUTPUT EXACTLY AS 3 NUMBERED QUESTIONS:
                            1. [Question 1 - Main Concept]
                            2. [Question 2 - Specific Process/Mechanism]
                            3. [Question 3 - Specific Detail/Application]
                            """
                            contents_payload.append(gen_prompt)

                            ticket_res = client.models.generate_content(
                                model=MODEL_NAME, 
                                contents=contents_payload,
                                config=types.GenerateContentConfig(temperature=0.0)
                            )
                            
                            fresh_db = load_db()
                            fresh_db["session_tickets"][session_key] = {
                                "title": lesson_title.strip() if lesson_title.strip() else "Unit Check-in",
                                "questions": ticket_res.text
                            }
                            save_db(fresh_db)
                            st.success(f"Exit Ticket Published Globally for {session_key}!")
                            st.rerun()
                    else:
                        st.error("Please upload a file or paste lesson notes to generate a ticket.")

            with col_right:
                st.markdown("<span class='ios-badge ios-badge-purple'>ACTIVE TICKET PREVIEW</span>", unsafe_allow_html=True)
                st.markdown(f"### Currently Active: {curr_ticket.get('title', 'None')}")
                
                if curr_ticket.get("questions"):
                    st.text_area(
                        "Questions Published to Students:",
                        value=curr_ticket["questions"],
                        height=220,
                        key="active_q_preview",
                        disabled=True
                    )
                else:
                    st.info("No active exit ticket published for this session yet.")

        # TAB 2: CLASS ANALYTICS & AI INSIGHTS
        with tab2:
            st.markdown("<div class='ios-spacer'></div>", unsafe_allow_html=True)
            st.markdown("<span class='ios-badge ios-badge-purple'>SESSION PERFORMANCE</span>", unsafe_allow_html=True)
            st.markdown(f"### Live Results for {st.session_state.active_course} — {st.session_state.active_period}")

            session_results = db.get("student_results", {}).get(session_key, [])

            if not session_results:
                st.info("No student responses submitted for this period yet.")
            else:
                df = pd.DataFrame(session_results)
                
                m1, m2 = st.columns(2)
                with m1:
                    st.metric("Total Submissions", len(df))
                with m2:
                    st.metric("Active Topic", curr_ticket.get("title", "N/A"))

                st.markdown("<div class='ios-spacer'></div>", unsafe_allow_html=True)
                st.dataframe(df[["Timestamp", "Student ID", "Score", "Misconception Summary"]], use_container_width=True)
                st.markdown("<div class='ios-spacer'></div>", unsafe_allow_html=True)
                
                if st.button("Generate AI Class Misconception Report 🤖"):
                    with st.spinner("Analyzing class submission trends..."):
                        summary_prompt = f"""
                        Analyze these student exit ticket summaries for the class period '{st.session_state.active_period}':
                        {df[['Student ID', 'Score', 'Misconception Summary']].to_json(orient='records')}

                        Provide a short, 3-bullet-point summary for the teacher:
                        1. Overall class understanding level.
                        2. Common errors or shared misconceptions identified.
                        3. Recommended follow-up activity or topic to re-teach next lesson.
                        """
                        report_res = client.models.generate_content(
                            model=MODEL_NAME, 
                            contents=summary_prompt,
                            config=types.GenerateContentConfig(temperature=0.0)
                        )
                        st.markdown(f"""
                        <div class="ios-feedback-card">
                            <h4 style="margin: 0 0 12px 0; color: #5856D6;">🤖 AI Teaching Assistant Insights</h4>
                            {report_res.text}
                        </div>
                        """, unsafe_allow_html=True)

        # TAB 3: MASTERY LOOP REGISTRY
        with tab3:
            st.markdown("<div class='ios-spacer'></div>", unsafe_allow_html=True)
            st.markdown("<span class='ios-badge ios-badge-orange'>REVISION TRACKER</span>", unsafe_allow_html=True)
            st.markdown(f"### Active Student Misconceptions ({st.session_state.active_period})")

            all_gaps = db.get("student_misconceptions", {}).get(session_key, {})

            if not all_gaps:
                st.info("No active misconceptions logged for this session.")
            else:
                for student, gaps in all_gaps.items():
                    with st.expander(f"👤 {student} ({len([g for g in gaps if not g.get('resolved')])} unresolved)"):
                        for idx, gap in enumerate(gaps):
                            status_badge = "✅ Resolved" if gap.get("resolved") else "🚨 Unresolved (Active in next ticket)"
                            st.write(f"**Lesson:** {gap.get('lesson')}")
                            st.write(f"**Identified Error:** {gap.get('misconception')}")
                            st.write(f"**Status:** {status_badge}")
                            st.divider()
