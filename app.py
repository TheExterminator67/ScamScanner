import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import re

# SETUP
st.set_page_config(page_title="Legal Guard", page_icon="🛡️")

if "GEMINI_KEY" not in st.secrets:
    st.error("❌ Missing GEMINI_KEY in Secrets!")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_KEY"])

# GEMINI MODEL
try:
    model = genai.GenerativeModel('gemini-3-flash-preview')
    st.sidebar.success("✅ AI Brain Connected")
except Exception as e:
    st.sidebar.error(f"❌ AI Connection Failed: {e}")

# UI
st.title("🛡️ Legal Guard: Scam Scanner")

uploaded_file = st.file_uploader("Upload a PDF to scan for scams", type=["pdf"])

if uploaded_file:
    with st.spinner("🕵️ AI Investigator is reading the document..."):
        try:
            # Extract text from PDF
            reader = PdfReader(uploaded_file)
            text = "".join([page.extract_text() for page in reader.pages])
            
            # FORMAT PROMPT
            prompt = f"""
            Analyze this document for scams. 
            YOU MUST START YOUR RESPONSE WITH THIS EXACT LINE:
            RISK SCORE: [number 1-10]
            
            Then, provide a detailed report including:
            - 🚩 Red Flags
            - ⚖️ Legal Loopholes
            - 💡 Advice
            
            Document text: {text[:8000]} 
            """
            
            # GENERATE ANALYSIS
            response = model.generate_content(prompt)
            full_analysis = response.text
            
            # COLOR-CODED OUTPUT BASED ON RISK SCORE
            score_match = re.search(r"RISK SCORE:\s*(\d+)", full_analysis)
            score = int(score_match.group(1)) if score_match else 5
            
            st.divider()
            
            # DISPLAY BASED ON RISK LEVEL
            if score >= 7:
                st.error(f"### 🚨 HIGH RISK (Score: {score}/10)")
                st.markdown(f":red[{full_analysis}]")
            elif score >= 4:
                st.warning(f"### ⚠️ MODERATE RISK (Score: {score}/10)")
                st.markdown(full_analysis)
            else:
                st.success(f"### ✅ LOW RISK (Score: {score}/10)")
                st.markdown(f":green[{full_analysis}]")
                st.snow()
                
        except Exception as e:
            if "429" in str(e):
                st.error("🚦 Google's Free Tier is busy. Wait 60 seconds and try again!")
            else:
                st.error(f"Error during analysis: {e}")

st.divider()
st.caption("Disclaimer: This is an AI tool, not a lawyer. Always read the fine print!")
