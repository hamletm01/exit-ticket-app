import streamlit as st
from google import genai
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
div[data-testid="stSidebar"] div[data-testid="stRadio"] > div {
    background: rgba(120, 120, 128, 0.12) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    border: none !important;
    gap: 4px !important;
}

div[data-testid="stSidebar"] div[data-testid="stRadio"] label {
    background: transparent !important;
    border-radius: 8px !important;
    padding: 8px 12px !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
    color: #1C1C1E !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    cursor: pointer !important;
}

div[data-testid="stSidebar"] div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) {
    background: #FFFFFF !important;
    color: #000000 !important;
    box-shadow: 0 3px 8px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.08) !important;
    font-weight: 600 !important;
}

div[data-testid="stSidebar"] div[data-testid="stRadio"] input[type="radio"] { display: none !important; }

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
