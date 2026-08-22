import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

# Setup Gemini Client
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

st.set_page_config(
    page_title="Student Smart Monitoring System",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 Student Smart Monitoring System (Gen AI Driven)")
st.markdown("Automated academic risk assessment, interactive editing, and AI interventions.")

DATA_FILE = "data/students.csv"

# Load Student Data
@st.cache_data
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        # Fallback default dataframe if file is missing
        return pd.DataFrame(columns=["student_id", "name", "attendance_pct", "math_score", "science_score", "english_score", "teacher_notes"])

try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading student data: {e}")
    st.stop()

# --- Interactive Data Editor Section ---
with st.expander("✏️ Edit / Manage Student Dataset Live", expanded=False):
    st.markdown("Make changes directly to the table below, add new rows, or delete records, then click **Save Changes**.")
    
    # st.data_editor allows inline editing
    edited_df = st.data_editor(df, num_rows="dynamic", key="student_editor")
    
    if st.button("💾 Save Changes to CSV"):
        try:
            # Ensure data directory exists
            os.makedirs("data", exist_ok=True)
            # Save to local CSV file
            edited_df.to_csv(DATA_FILE, index=False)
            st.success("Dataset successfully updated and saved!")
            st.rerun()
        except Exception as err:
            st.error(f"Failed to save changes: {err}")

# Refresh dataframe reference to edited version if active
df = edited_df

# Sidebar Student Selection
st.sidebar.header("Navigation")
if df.empty:
    st.warning("No student records available. Please add some rows in the editor above.")
    st.stop()

student_names = df["name"].tolist()
selected_student = st.sidebar.selectbox("Select a Student:", student_names)

# Get Selected Student Details
student_info = df[df["name"] == selected_student].iloc[0]

# Metrics Display
col1, col2, col3, col4 = st.columns(4)
col1.metric("Attendance Rate", f"{student_info.get('attendance_pct', 0)}%")
col2.metric("Math Score", f"{student_info.get('math_score', 0)}/100")
col3.metric("Science Score", f"{student_info.get('science_score', 0)}/100")
col4.metric("English Score", f"{student_info.get('english_score', 0)}/100")

# Academic Risk Analysis
attendance = float(student_info.get('attendance_pct', 0))
math = float(student_info.get('math_score', 0))
science = float(student_info.get('science_score', 0))
english = float(student_info.get('english_score', 0))

is_at_risk = attendance < 75 or math < 50 or science < 50 or english < 50

if is_at_risk:
    st.warning("⚠️ **Risk Flag:** Student is currently identified as Academic At-Risk.")
else:
    st.success("✅ **Good Standing:** Student meets performance benchmarks.")

st.subheader(f"AI Performance Report: {student_info['name']}")
st.info(student_info.get('teacher_notes', 'No notes provided.'))

# Gen AI Advisory Generation
if st.button("Generate AI Advisory & Email Draft"):
    if not client:
        st.error("Gemini API Key is missing. Please check your `.env` file or Streamlit Secrets.")
    else:
        prompt = f"""
        You are an educational AI assistant analyzing student academic performance.

        Student Details:
        - Name: {student_info['name']}
        - Attendance: {student_info.get('attendance_pct')}%
        - Math Score: {student_info.get('math_score')}
        - Science Score: {student_info.get('science_score')}
        - English Score: {student_info.get('english_score')}
        - Teacher Notes: {student_info.get('teacher_notes')}

        Please provide:
        1. A 3-step actionable study plan tailored to help this student improve.
        2. A professional, polite email draft to the student's parents summarizing their progress, highlighting key areas needing attention, and offering supportive next steps.
        """

        with st.spinner("Analyzing student metrics with Gemini..."):
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt
                )
                st.markdown(response.text)
            except Exception as err:
                st.error(f"Error calling Gemini API: {err}")