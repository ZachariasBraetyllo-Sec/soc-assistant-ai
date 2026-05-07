import streamlit as st
import os
import google.generativeai as genai
from openai import OpenAI
from dotenv import load_dotenv

# 1. Load API keys
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

# 2. Setup Models
genai.configure(api_key=GOOGLE_API_KEY)
gemini_model = genai.GenerativeModel('gemini-2.5-flash')

# NIM uses the OpenAI-compatible library
nim_client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=NVIDIA_API_KEY
)

# 3. Streamlit UI
st.set_page_config(page_title="SOC Assistant", layout="wide")
st.title("🛡️ AI SOC Assistant")
st.subheader("Automated Threat Intel Summarization & Scoring")

report_text = st.text_area("Paste Threat Report Text Here:", height=300)

if st.button("Analyze Report"):
    if report_text:
        with st.spinner("Gemini is summarizing report..."):
            # TASK 1: Summarization (Gemini's strength)
            summary_prompt = f"Extract the key Indicators of Compromise (IOCs), threat actors, and attack vectors from this report: {report_text}"
            summary_response = gemini_model.generate_content(summary_prompt)
            summary = summary_response.text

        with st.spinner("NVIDIA NIM is scoring risk..."):
            # TASK 2: Classification (NIM's strength)
            # We send Gemini's summary to Mistral-Large for a high-precision score
            nim_response = nim_client.chat.completions.create(
                model="mistralai/mistral-large-3-675b-instruct-2512",
                messages=[{"role": "user", "content": f"Based on this summary, provide a Risk Score (1-10) and Industry Impact. Summary: {summary}"}],
                temperature=0.2,
                max_tokens=500
            )
            analysis = nim_response.choices[0].message.content

        # 4. Display Results
        col1, col2 = st.columns(2)
        with col1:
            st.success("### Report Summary (via Gemini)")
            st.write(summary)
        
        with col2:
            st.warning("### Risk Analysis (via NVIDIA NIM)")
            st.write(analysis)
    else:
        st.error("Please paste a report first!")