import streamlit as st
import json
import os
from google import genai
from google.genai import types

# -----------------------------------------------------------------------------
# SETUP & INITIALIZATION
# -----------------------------------------------------------------------------
DB_FILE = "db.json"
MODEL_NAME = "gemini-2.5-flash"

# Initialize Gemini Client (Ensure GEMINI_API_KEY is in st.secrets or environment)
client = genai.Client()

def load_db():
    if not os.path.exists(DB_FILE):
        return {"session_tickets": {}}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

# -----------------------------------------------------------------------------
# STREAMLIT UI: CURRICULUM AUTHORING
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Curriculum Authoring", layout="wide")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Curriculum Authoring")
    st.header("Create Ticket for Period 1 - Sep 01")
    
    lesson_title = st.text_input("Lesson Title / Unit Topic:", placeholder="No Published Ticket")
    
    uploaded_file = st.file_uploader("Upload Lesson Content (PDF, DOCX, TXT):", type=["pdf", "docx", "txt"])
    
    raw_notes = st.text_area("Or Paste Syllabus Notes / Outline:", placeholder="Water", height=120)
    
    if st.button("Generate & Publish Ticket 📢", type="primary"):
        session_key = "Period 1 - Sep 01"
        contents_payload = []
        
        with st.spinner("✨ Processing document with Gemini vision & authoring ticket..."):
            # 1. Direct Multimodal Attachment (PDF / Images / Text Files)
            if uploaded_file is not None:
                file_bytes = uploaded_file.getvalue()
                mime_type = uploaded_file.type
                
                # Fallback for standard text/docx if mime type isn't automatically detected
                if not mime_type:
                    if uploaded_file.name.endswith(".pdf"):
                        mime_type = "application/pdf"
                    elif uploaded_file.name.endswith(".txt"):
                        mime_type = "text/plain"
                    else:
                        mime_type = "application/octet-stream"

                # Send raw bytes directly to Gemini's visual document parser
                contents_payload.append(
                    types.Part.from_bytes(
                        data=file_bytes,
                        mime_type=mime_type,
                    )
                )

            # 2. Append pasted text notes if provided
            if raw_notes.strip():
                contents_payload.append(f"Additional Teacher Notes:\n{raw_notes.strip()}")

            # 3. Prompt definition targeting body content only
            if contents_payload:
                gen_prompt = """
                You are a classroom teacher creating an exit ticket quiz for your students based ONLY on the primary educational content in the attached document.

                STRICT RULES FOR QUESTION GENERATION:
                1. NO METADATA/FORM QUESTIONS: Completely ignore system tags, page metadata, hidden form fields, or structural numbers (e.g., sequence codes, form IDs).
                2. NO REPETITION: Each of the 3 questions MUST test a COMPLETELY DIFFERENT concept, definition, detail, or process from the lesson content.
                3. QUESTION DIVERSITY:
                   - Question 1: Ask about the main definition or primary concept presented.
                   - Question 2: Ask about a specific mechanism, process, stage, or relationship described in the body.
                   - Question 3: Ask about a specific detail, key term, diagram label, or real-world application mentioned.
                4. Phrase questions naturally as direct classroom checks for student understanding.

                FORMAT OUTPUT EXACTLY AS 3 NUMBERED QUESTIONS:
                1. [Question 1]
                2. [Question 2]
                3. [Question 3]
                """
                
                contents_payload.append(gen_prompt)

                try:
                    ticket_res = client.models.generate_content(
                        model=MODEL_NAME,
                        contents=contents_payload,
                        config=types.GenerateContentConfig(
                            temperature=0.0
                        )
                    )

                    # Update local database
                    db = load_db()
                    db["session_tickets"][session_key] = {
                        "title": lesson_title.strip() if lesson_title.strip() else "Unit Check-in",
                        "questions": ticket_res.text
                    }
                    save_db(db)

                    st.success("Exit Ticket Published Successfully!")
                    st.rerun()

                except Exception as e:
                    st.error(f"Error generating ticket: {e}")
            else:
                st.warning("Please upload a file or enter text notes to generate a ticket.")

with col2:
    st.subheader("Active Ticket Preview")
    db = load_db()
    active_ticket = db.get("session_tickets", {}).get("Period 1 - Sep 01")

    if active_ticket:
        st.header(f"Currently Active: {active_ticket.get('title')}")
        st.write("Questions Published to Students:")
        st.info(active_ticket.get("questions"))
    else:
        st.header("Currently Active: No Published Ticket")
        st.write("Questions Published to Students:")
        st.text_area("", value="No published ticket yet.", height=200, disabled=True)
