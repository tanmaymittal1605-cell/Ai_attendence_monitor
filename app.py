import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

# Setup Gemini Client
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

st.set_page_config(
    page_title="Student Smart Monitoring System",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 Student Smart Monitoring System (Gen AI Driven)")
st.markdown("Automated academic risk assessment and personalized AI interventions.")

# Load Student Data
@st.cache_data
def load_data():
    return pd.read_csv("data/students.csv")

try:
    df = load_data()
except Exception as e:
    st.error("Error loading `data/students.csv`. Please ensure the file exists.")
    st.stop()

# Sidebar Setup
st.sidebar.header("Navigation & Settings")
selected_student_name = st.sidebar.selectbox("Select a Student:", df["name"].tolist())

# Get Selected Student Details
student = df[df["name"] == selected_student_name].iloc[0]

# Display Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Attendance", f"{student['attendance_pct']}%")
col2.metric("Math Score", f"{student['math_score']}/100")
col3.metric("Science Score", f"{student['science_score']}/100")
col4.metric("English Score", f"{student['english_score']}/100")

# Risk Assessment Logic
is_risk = student['attendance_pct'] < 75 or (student['math_score'] + student['science_score'] + student['english_score']) / 3 < 50

if is_risk:
    st.error("⚠️ **Risk Flag:** Student is flagged for low attendance or poor academic standing.")
else:
    st.success("✅ **Good Standing:** Student meets performance benchmarks.")

st.markdown("---")
st.subheader(f"AI Performance Report: {student['name']}")

# AI Analysis Action
if st.button("Generate AI Advisory & Email Draft"):
    if not client:
        st.error("API Key not found! Please set `GEMINI_API_KEY` in your `.env` file.")
    else:
        with st.spinner("Analyzing student profile with Gen AI..."):
            prompt = f"""
            You are an expert AI educational counselor. Analyze the following student record:
            - Name: {student['name']}
            - Attendance Rate: {student['attendance_pct']}%
            - Math Score: {student['math_score']}
            - Science Score: {student['science_score']}
            - English Score: {student['english_score']}
            - Teacher Notes: {student['teacher_notes']}

            Please provide:
            1. Executive Summary of Academic Health
            2. Three Specific Action Steps to Help the Student
            3. A Professional, Empathetic Draft Email to the Parent/Guardian
            """
            
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt
                )
                st.markdown(response.text)
            except Exception as err:
                st.error(f"Error calling Gemini API: {err}")

# Data Table Display
with st.expander("View Full Class Dataset"):
    st.dataframe(df)