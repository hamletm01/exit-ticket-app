import streamlit as st
import sqlite3
import pypdf
import docx
import json
import re
from datetime import datetime

# Page Config
st.set_page_config(page_title="Exit Ticket Studio", page_icon="🎓", layout="wide")

# 1. Imports & SDK Setup
try:
    from google import genai
    from google.genai import types
except ImportError as e:
    st.error(f"Import Error: {e}. Please ensure 'google-genai' is listed in your requirements.txt.")
    st.stop()

# 2. Database Initialization (SQLite)
DB_FILE = "exit_ticket_app.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sessions (
                    session_key TEXT PRIMARY KEY,
                    course TEXT,
                    period TEXT,
                    title TEXT,
                    questions TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS submissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_key TEXT,
                    student_name TEXT,
                    score TEXT,
                    timestamp TEXT,
                    raw_feedback TEXT
                )''')
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

# Seed default database entry if empty
if not run_query("SELECT * FROM sessions", fetchall=True):
    default_q = "1. Explain the primary function of photosynthesis.\n2. What are the key outputs of cellular respiration?\n3. How do plants convert light energy into chemical energy?"
    run_query(
        "INSERT INTO sessions (session_key, course, period, title, questions) VALUES (?, ?, ?, ?, ?)",
        ("Biology::Period 1", "Biology", "Period 1", "Photosynthesis & Respiration", default_q),
        commit=True
    )

# 3. API Client Connection
if "GEMINI_API_KEY" in st.secrets:
    api_key = str(st.secrets["GEMINI_API_KEY"]).strip().strip('"').strip("'")
    client = genai.Client(api_key=api_key)
else:
    st.error("⚠️ GEMINI_API_KEY is missing in your Streamlit secrets (.streamlit/secrets.toml).")
    st.stop()

# 4. Helper Functions & Robust Execution
def sanitize_text(text):
    if not text:
        return ""
    return re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', str(text)).strip()

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
        raise ValueError("Cannot send an empty prompt.")

    # Validated endpoints for google-genai package
    models_to_try = ["gemini-2.5-flash", "gemini-2.0-flash"]
    
    config_dict = {"temperature": 0.2}
    if system_instruction:
        config_dict["system_instruction"] = sanitize_text(system_instruction)
    if response_json:
        config_dict["response_mime_type"] = "application/json"
        
    config = types.GenerateContentConfig(**config_dict)
    
    last_err = None
    for model_id in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_id,
                contents=clean_prompt,
                config=config
            )
            return response.text
        except Exception as e:
            last_err = e
            continue
            
    raise RuntimeError(f"API Call Failed: {last_err}")

# 5. Application Interface
st.title("🎓 Exit Ticket Studio")
app_mode = st.sidebar.radio("Navigation", ["🎓 Student Portal", "👨‍🏫 Teacher Studio"])

existing_sessions = run_query("SELECT session_key, course, period FROM sessions", fetchall=True)
courses = list(set([s[1] for s in existing_sessions])) if existing_sessions else ["Biology"]

col_c, col_p = st.columns(2)
with col_c:
    selected_course = st.selectbox("📚 Course", options=courses)

available_periods = [s[2] for s in existing_sessions if s[1] == selected_course]
if not available_periods:
    available_periods = ["Period 1"]

with col_p:
    selected_period = st.selectbox("📅 Session / Period", options=available_periods)

active_session_key = f"{selected_course}::{selected_period}"
active_session = run_query("SELECT title, questions FROM sessions WHERE session_key = ?", (active_session_key,), fetchone=True)

active_title = active_session[0] if active_session else "Untitled Lesson"
active_questions = active_session[1] if active_session else ""

# ------------------------------------------
# MODE 1: STUDENT PORTAL
# ------------------------------------------
if app_mode == "🎓 Student Portal":
    st.subheader(f"Lesson: {active_title}")
    
    if not active_questions:
        st.info("No active exit ticket published for this session yet.")
    else:
        student_name = st.text_input("Enter Student Name or ID to start:").strip().title()
        
        if student_name:
            unresolved = run_query(
                "SELECT id, lesson, misconception FROM misconceptions WHERE student_name = ? AND resolved = 0 ORDER BY id DESC LIMIT 1",
                (student_name,),
                fetchone=True
            )
            
            mastery_question = None
            if unresolved:
                st.warning(f"🔄 **Mastery Revision Active:** Re-testing concept from '{unresolved[1]}'")
                try:
                    mastery_question = safe_gemini_call(f"Generate 1 short review question for a student testing: '{unresolved[2]}'")
                except Exception:
                    mastery_question = None
            
            base_q_list = [q.strip() for q in active_questions.split("\n") if q.strip()]
            
            with st.form("student_ticket_form"):
                answers = []
                all_q = []
                
                if mastery_question:
                    st.markdown(f"**[Revision] {mastery_question}**")
                    ans_m = st.text_area("Revision Answer:", key="ans_m")
                    answers.append(ans_m)
                    all_q.append(f"[Revision] {mastery_question}")
                
                for idx, q_text in enumerate(base_q_list):
                    st.markdown(f"**Q{idx+1}: {q_text}**")
                    ans = st.text_area(f"Answer for Q{idx+1}:", key=f"ans_{idx}")
                    answers.append(ans)
                    all_q.append(q_text)
                
                submit = st.form_submit_button("Submit Exit Ticket 🚀")
                
                if submit:
                    if any(not a.strip() for a in answers):
                        st.warning("Please fill out all questions before submitting.")
                    else:
                        with st.spinner("Analyzing responses..."):
                            payload = "\n".join([f"Q: {q}\nA: {a}" for q, a in zip(all_q, answers)])
                            eval_prompt = f"""
                            Evaluate student ({student_name}) for lesson '{active_title}'.
                            Submission:
                            {payload}

                            Return JSON ONLY:
                            {{
                                "score": "X/{len(all_q)}",
                                "correct_summary": "Summary of correct work.",
                                "incorrect_summary": "Summary of errors or missing concepts.",
                                "revision_topics": ["Topic 1"],
                                "teacher_question": "One targeted question for the student to ask their teacher tomorrow.",
                                "has_misconception": false,
                                "misconception_details": null
                            }}
                            """
                            try:
                                raw_json = safe_gemini_call(eval_prompt, response_json=True)
                                res = json.loads(raw_json)
                                
                                now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                                run_query(
                                    "INSERT INTO submissions (session_key, student_name, score, timestamp, raw_feedback) VALUES (?, ?, ?, ?, ?)",
                                    (active_session_key, student_name, res.get("score"), now_str, raw_json),
                                    commit=True
                                )
                                
                                if unresolved and not res.get("has_misconception", False):
                                    run_query("UPDATE misconceptions SET resolved = 1 WHERE id = ?", (unresolved[0],), commit=True)
                                
                                if res.get("has_misconception") and res.get("misconception_details"):
                                    run_query(
                                        "INSERT INTO misconceptions (session_key, student_name, lesson, misconception, resolved) VALUES (?, ?, ?, ?, 0)",
                                        (active_session_key, student_name, active_title, res.get("misconception_details")),
                                        commit=True
                                    )
                                
                                st.success(f"Score: {res.get('score')}")
                                st.markdown(f"**✅ Strengths:** {res.get('correct_summary')}")
                                st.markdown(f"**🔍 Areas for Growth:** {res.get('incorrect_summary')}")
                                st.info(f"💡 **Ask your teacher tomorrow:** \"{res.get('teacher_question')}\"")
                            except Exception as e:
                                st.error(f"Evaluation failed: {e}")

# ------------------------------------------
# MODE 2: TEACHER STUDIO
# ------------------------------------------
else:
    st.subheader("👨‍🏫 Teacher Studio")
    tab1, tab2 = st.tabs(["📝 Author Ticket", "📊 Student Analytics"])
    
    with tab1:
        lesson_title = st.text_input("Lesson Title:", value=active_title)
        uploaded_file = st.file_uploader("Upload Content File (PDF, DOCX, TXT):", type=["pdf", "docx", "txt"])
        raw_notes = st.text_area("Or Paste Syllabus Notes / Text:")
        
        if st.button("Generate & Publish Ticket 📢"):
            combined = ""
            if uploaded_file:
                combined += extract_file_content(uploaded_file) + "\n"
            if raw_notes:
                combined += sanitize_text(raw_notes)
                
            if not combined.strip():
                st.error("Please provide lesson notes or upload a file.")
            else:
                with st.spinner("Generating exit ticket..."):
                    gen_prompt = f"Create 3 exit ticket questions based on this material:\n{combined[:7000]}\nFormat exactly as:\n1. [Q1]\n2. [Q2]\n3. [Q3]"
                    try:
                        q_out = safe_gemini_call(gen_prompt)
                        run_query(
                            "INSERT OR REPLACE INTO sessions (session_key, course, period, title, questions) VALUES (?, ?, ?, ?, ?)",
                            (active_session_key, selected_course, selected_period, lesson_title, q_out),
                            commit=True
                        )
                        st.success("Exit Ticket Published Successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Generation failed: {e}")
                        
    with tab2:
        subs = run_query("SELECT student_name, score, timestamp, raw_feedback FROM submissions WHERE session_key = ?", (active_session_key,), fetchall=True)
        if not subs:
            st.info("No student submissions recorded for this session yet.")
        else:
            for sname, score, ts, raw in subs:
                with st.expander(f"👤 {sname} — Score: {score} ({ts})"):
                    try:
                        data = json.loads(raw)
                        st.write(f"**Strengths:** {data.get('correct_summary')}")
                        st.write(f"**Needs Work:** {data.get('incorrect_summary')}")
                        st.write(f"**Teacher Question:** {data.get('teacher_question')}")
                    except Exception:
                        st.text(raw)
