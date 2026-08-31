import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="Teacher Studio",
    page_icon="🎓",
    layout="wide"
)

# 2. Inject Custom CSS for Full-Width Pill Navigation
st.html(
    """
    <style>
    /* Force main container to use maximum width */
    .stMainBlockContainer {
        max-width: 100% !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }

    /* Target both native segmented controls and st.radio wrappers */
    div[data-testid="stSegmentedControl"],
    div[data-testid="stRadio"],
    div[class*="st-key-teacher_studio_menu"] {
        width: 100% !important;
        max-width: 100% !important;
        display: flex !important;
    }

    /* Enforce full width on the inner item container */
    div[data-testid="stSegmentedControl"] > div,
    div[role="radiogroup"] {
        width: 100% !important;
        display: flex !important;
        flex-direction: row !important;
        background-color: rgba(118, 118, 128, 0.12) !important;
        border-radius: 12px !important;
        padding: 4px !important;
        gap: 4px !important;
        box-sizing: border-box !important;
    }

    /* Stretch each menu button equally across the page width */
    div[data-testid="stSegmentedControl"] button,
    div[role="radiogroup"] > label {
        flex: 1 1 0% !important;
        width: 100% !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        padding: 8px 16px !important;
        border-radius: 8px !important;
        border: none !important;
        background: transparent !important;
        color: #1C1C1E !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        cursor: pointer !important;
        transition: all 0.2s ease-in-out !important;
        white-space: nowrap !important;
    }

    /* Hide standard radio dot elements */
    div[role="radiogroup"] > label > div:first-child {
        display: none !important;
    }

    /* Selected tab styling */
    div[data-testid="stSegmentedControl"] button[aria-selected="true"],
    div[role="radiogroup"] > label:has(input:checked) {
        background-color: #FFFFFF !important;
        color: #5856D6 !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12) !important;
    }
    </style>
    """
)

# 3. Application UI
st.title("Teacher Studio")

menu_options = [
    "Overview",
    "Lesson Planner",
    "Assessments",
    "Student Analytics",
    "Settings"
]

# Render menu (using key="teacher_studio_menu" for CSS binding)
selected_tab = st.radio(
    label="Navigation",
    options=menu_options,
    index=0,
    horizontal=True,
    label_visibility="collapsed",
    key="teacher_studio_menu"
)

st.divider()

# 4. Content Area
st.subheader(f"Active Section: {selected_tab}")
st.write(f"Displaying content area for **{selected_tab}**.")
