import streamlit as st
from google import genai
from google.genai import types
import sqlite3
import pypdf
import docx
import json
import re
from datetime import datetime

# ==========================================
# 1. DATABASE INITIALIZATION (SQLite Native)
# ==========================================
DB_FILE = "exit_ticket_app.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Courses & Sessions
    c.execute('''CREATE TABLE IF NOT EXISTS sessions (
                    session_key TEXT PRIMARY KEY,
                    course TEXT,
                    period TEXT,
                    title TEXT,
                    questions TEXT
                )''')
    # Student Submissions
    c.execute('''CREATE TABLE IF NOT EXISTS submissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_key TEXT,
                    student_name TEXT,
                    score TEXT,
                    timestamp TEXT,
                    raw_feedback TEXT
                )''')
    # Mastery / Misconception Loop
    c.execute('''CREATE TABLE IF NOT EXISTS misconceptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_key TEXT,
                    student_name TEXT,
                    lesson TEXT,
                    misconception TEXT,
                    resolved INTEGER DEFAULT 0
                )''')
    conn.commit()
    conn.close()

init_db()

# Database Helper Functions
def run_query(query, params=(), fetchone=False, fetchall=False, commit=False):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(query, params)
    data = None
    if fetchone:
        data = c.fetchone()
    elif fetchall:
        data = c.fetchall()
    if commit:
        conn.commit()
    conn.close()
    return data

# Seed default session if database is completely empty
if not run_query("SELECT * FROM sessions", fetchall=True):
    default_q = "1. Explain the primary function of photosynthesis.\n2. What are the key outputs of cellular respiration?\n3. How do plants convert light energy to chemical energy?"
    run_query(
        "INSERT INTO sessions (session_key, course, period, title, questions) VALUES (?, ?, ?, ?, ?)",
        ("Earth Science::Period 1", "Earth Science", "Period 1", "Photosynthesis & Respiration", default_q),
        commit=True
    )

# ==========================================
# 2. PAGE CONFIG & API INITIALIZATION
# ==========================================
st.set_page_config(page_title="Exit Ticket Studio", page_icon="🎓", layout="wide")

if "GEMINI_API_KEY" in st.secrets:
    api_key = str(st.secrets["GEMINI_API_KEY"]).strip().strip('"').strip("'")
    client = genai.Client(api_key=api_key)
else:
    st.error("⚠️ API Key missing in Streamlit Secrets.")
    st.stop()

# ==========================================
# 3. ROBUST UTILITIES & GEMINI API CALL
# ==========================================
def sanitize_text(text):
    if not text:
        return ""
    # Remove control characters and non-printable bytes that trigger 4xx ClientError
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', str(text))
    return text.strip()

def extract_file_content(uploaded_file):
    text = ""
    try:
        if uploaded_file.name.endswith(".pdf"):
            reader = pypdf.PdfReader(uploaded_file)
            for page in reader.pages:
                text += (page.extract_text() or "") + "\n"
        elif uploaded_file.name.endswith(".docx"):
            doc = docx.Document(uploaded_file)
            for para in doc.paragraphs:
                text += para.text + "\n"
        elif uploaded_file.name.endswith(".txt"):
            text = uploaded_file.read().decode("utf-8")
    except Exception as e:
        st.error(f"Error reading file: {e}")
    return sanitize_text(text)

def safe_gemini_call(prompt, system_instruction=None, response_json=False):
    clean_prompt = sanitize_text(prompt)
    if not clean_prompt:
        raise ValueError("Cannot process empty prompt payload.")

    models_to_try = ["gemini-2.0-flash", "gemini-1.5-flash"]
    config_args = {"temperature": 0.0}
    
    if system_instruction:
        config_args["system_instruction"] = sanitize_text(system_instruction)
    if response_json:
        config_args["response_mime_type"] = "application/json"
        
    config = types.GenerateContentConfig(**config_args)
    
    last_err = None
    for model in models_to_try:
        try:
            res = client.models.generate_content(
                model=model,
                contents=clean_prompt,
                config=config
            )
            return res.text
        except Exception as e:
            last_err = e
            continue
    raise RuntimeError(f"API Failure across models: {last_err}")

# ==========================================
# 4. APP NAVIGATION & SCOPE SELECTORS
# ==========================================
st.title("🎓 Exit Ticket Studio")
app_mode = st.sidebar.radio("Navigation", ["🎓 Student Portal", "👨‍🏫 Teacher Studio"])

# Get available sessions from database
existing_sessions = run_query("SELECT session_key, course, period FROM sessions", fetchall=True)
courses = list(set([s[1] for s in existing_sessions])) if existing_sessions else ["Earth Science"]

col_c, col_p = st.columns(2)
with col_c:
    selected_course = st.selectbox("📚 Select Course", options=courses)

available_periods = [s[2] for s in existing_sessions if s[1] == selected_course]
if not available_periods:
    available_periods = ["Period 1"]

with col_p:
    selected_period = st.selectbox("📅 Select Session / Period", options=available_periods)

active_session_key = f"{selected_course}::{selected_period}"
active_session = run_query("SELECT title, questions FROM sessions WHERE session_key = ?", (active_session_key,), fetchone=True)

if not active_session:
    active_title = "No Published Ticket"
    active_questions = ""
else:
    active_title, active_questions = active_session

# ==========================================
# MODE 1: STUDENT PORTAL
# ==========================================
if app_mode == "🎓 Student Portal":
    st.subheader(f"Lesson: {active_title}")
    
    if not active_questions:
        st.info("No active exit ticket published for this session yet. Please ask your teacher to publish one.")
    else:
        student_name = st.text_input("Enter Student Name / ID to begin:", placeholder="e.g. Alex Smith").strip().title()
        
        if student_name:
            # Check for unresolved misconceptions in the database (Mastery Loop)
            unresolved = run_query(
                "SELECT id, lesson, misconception FROM misconceptions WHERE student_name = ? AND resolved = 0 ORDER BY id DESC LIMIT 1",
                (student_name,),
                fetchone=True
            )
            
            mastery_question = None
            if unresolved:
                m_id, m_lesson, m_concept = unresolved
                st.warning(f"🔄 **Mastery Revision Active:** Re-testing concept from prior lesson ('{m_lesson}')")
                
                with st.spinner("Generating personalized revision question..."):
                    m_prompt = f"Create 1 direct review question testing: '{m_concept}'. Keep it concise and supportive."
                    try:
                        mastery_question = safe_gemini_call(m_prompt)
                    except Exception:
                        mastery_question = None
            
            # Parsing main questions
            base_q_list = [q.strip() for q in active_questions.split("\n") if q.strip()]
            
            with st.form("student_ticket_form"):
                answers = []
                all_q = []
                
                if mastery_question:
                    st.markdown(f"**[Revision Question] {mastery_question}**")
                    ans_m = st.text_area("Your Revision Answer:", key="ans_m")
                    answers.append(ans_m)
                    all_q.append(f"[Revision] {mastery_question}")
                
                for idx, q_text in enumerate(base_q_list):
                    st.markdown(f"**Q{idx+1}: {q_text}**")
                    ans = st.text_area(f"Your Answer for Q{idx+1}:", key=f"ans_{idx}")
                    answers.append(ans)
                    all_q.append(q_text)
                
                submit = st.form_submit_button("Submit Exit Ticket 🚀")
                
                if submit:
                    if any(not a.strip() for a in answers):
                        st.warning("Please fill in all answers before submitting.")
                    else:
                        with st.spinner("Analyzing responses and compiling diagnostic feedback..."):
                            payload = "\n".join([f"Q: {q}\nA: {a}" for q, a in zip(all_q, answers)])
                            
                            eval_prompt = f"""
                            Evaluate student ({student_name})'s submission for '{active_title}'.
                            Submission:
                            {payload}

                            Return JSON ONLY:
                            {{
                                "score": "X/{len(all_q)}",
                                "correct_summary": "What they understood well.",
                                "incorrect_summary": "What was wrong or missing.",
                                "revision_topics": ["Topic 1", "Topic 2"],
                                "teacher_question": "One specific question for the student to ask their teacher tomorrow.",
                                "has_misconception": true/false,
                                "misconception_details": "1 sentence description of core error if present, else null"
                            }}
                            """
                            
                            try:
                                raw_json = safe_gemini_call(
                                    prompt=eval_prompt,
                                    system_instruction="You are a supportive high school tutor.",
                                    response_json=True
                                )
                                res = json.loads(raw_json)
                                
                                # Store submission in SQLite
                                now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                                run_query(
                                    "INSERT INTO submissions (session_key, student_name, score, timestamp, raw_feedback) VALUES (?, ?, ?, ?, ?)",
                                    (active_session_key, student_name, res.get("score"), now_str, raw_json),
                                    commit=True
                                )
                                
                                # Process Mastery Loop state
                                if mastery_question and not res.get("has_misconception", False):
                                    run_query("UPDATE misconceptions SET resolved = 1 WHERE id = ?", (unresolved[0],), commit=True)
                                
                                if res.get("has_misconception") and res.get("misconception_details"):
                                    run_query(
                                        "INSERT INTO misconceptions (session_key, student_name, lesson, misconception, resolved) VALUES (?, ?, ?, ?, 0)",
                                        (active_session_key, student_name, active_title, res.get("misconception_details")),
                                        commit=True
                                    )
                                
                                # Render feedback
                                st.success(f"Evaluation Complete! Score: {res.get('score')}")
                                st.markdown("### 📊 Diagnostic Feedback")
                                st.markdown(f"**✅ Strong Points:** {res.get('correct_summary')}")
                                st.markdown(f"**🔍 Needs Attention:** {res.get('incorrect_summary')}")
                                
                                st.markdown("**📖 Topics to Revise:**")
                                for t in res.get("revision_topics", []):
                                    st.write(f"- {t}")
                                
                                st.info(f"💡 **Ask your teacher tomorrow:** \"{res.get('teacher_question')}\"")
                                
                            except Exception as e:
                                st.error(f"Failed to process evaluation: {e}")

# ==========================================
# MODE 2: TEACHER STUDIO
# ==========================================
else:
    st.subheader("👨‍🏫 Teacher Authoring & Analytics")
    tab1, tab2, tab3 = st.tabs(["📝 Author Ticket", "📊 Student Analytics", "🔄 Mastery Registry"])
    
    with tab1:
        st.write(f"### Target Session: {selected_course} — {selected_period}")
        
        with st.expander("➕ Create New Course or Session"):
            n_course = st.text_input("New Course Name:").strip()
            n_period = st.text_input("New Session/Period Name (e.g., Period 3 - Oct 12):").strip()
            if st.button("Add Session"):
                if n_course and n_period:
                    s_key = f"{n_course}::{n_period}"
                    run_query(
                        "INSERT OR REPLACE INTO sessions (session_key, course, period, title, questions) VALUES (?, ?, ?, ?, ?)",
                        (s_key, n_course, n_period, "Untitled Unit", ""),
                        commit=True
                    )
                    st.success(f"Created session {s_key}")
                    st.rerun()

        lesson_title = st.text_input("Unit / Lesson Title:", value=active_title)
        uploaded_file = st.file_uploader("Upload Content File (PDF, DOCX, TXT):", type=["pdf", "docx", "txt"])
        raw_notes = st.text_area("Or Paste Syllabus Notes / Text:")
        
        if st.button("Generate & Publish Ticket 📢"):
            combined_text = ""
            if uploaded_file:
                combined_text += extract_file_content(uploaded_file) + "\n"
            if raw_notes.strip():
                combined_text += sanitize_text(raw_notes)
                
            if not combined_text.strip():
                st.error("Please provide lesson notes or upload a file.")
            else:
                with st.spinner("Synthesizing content into exit ticket questions..."):
                    gen_prompt = f"""
                    Create 3 distinct questions based on this material:
                    {combined_text[:7000]}

                    Format output exactly as 3 numbered lines:
                    1. [Question 1]
                    2. [Question 2]
                    3. [Question 3]
                    """
                    
                    try:
                        q_output = safe_gemini_call(
                            prompt=gen_prompt,
                            system_instruction="You are an expert high school teacher creating direct assessment questions."
                        )
                        
                        run_query(
                            "INSERT OR REPLACE INTO sessions (session_key, course, period, title, questions) VALUES (?, ?, ?, ?, ?)",
                            (active_session_key, selected_course, selected_period, lesson_title, q_output),
                            commit=True
                        )
                        
                        st.success(f"Successfully published to {active_session_key}!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Generation failed: {e}")
                        
    with tab2:
        st.write(f"### Submissions for {active_session_key}")
        subs = run_query(
            "SELECT student_name, score, timestamp, raw_feedback FROM submissions WHERE session_key = ? ORDER BY id DESC",
            (active_session_key,),
            fetchall=True
        )
        
        if not subs:
            st.info("No student responses recorded for this session yet.")
        else:
            for student, score, ts, raw in subs:
                with st.expander(f"👤 {student} — Score: {score} ({ts})"):
                    try:
                        data = json.loads(raw)
                        st.write(f"**Strengths:** {data.get('correct_summary')}")
                        st.write(f"**Needs Work:** {data.get('incorrect_summary')}")
                        st.write(f"**Teacher Question:** {data.get('teacher_question')}")
                    except Exception:
                        st.write(raw)
                        
    with tab3:
        st.write(f"### Active Misconceptions Tracked across Sessions")
        gaps = run_query(
            "SELECT student_name, lesson, misconception, resolved FROM misconceptions ORDER BY id DESC",
            fetchall=True
        )
        if not gaps:
            st.info("No active misconceptions logged in the system.")
        else:
            for student, lesson, misc, res in gaps:
                status = "✅ Resolved" if res == 1 else "🚨 Active (Will trigger revision on next entry)"
                st.write(f"**Student:** {student} | **Lesson:** {lesson}")
                st.write(f"**Misconception:** {misc}")
                st.write(f"**Status:** {status}")
                st.divider()
