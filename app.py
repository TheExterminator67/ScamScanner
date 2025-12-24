import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import re

# SETUP
st.set_page_config(page_title="Legal Guard Pro", page_icon="🛡️", layout="wide")

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

# UI BRANDING
st.title("🛡️ Legal Guard: :blue[Pro Scanner]")
st.markdown("### Detects scams, traps, and predatory language in seconds.")

uploaded_file = st.file_uploader("Upload a PDF contract", type=["pdf"])

if uploaded_file:
    with st.spinner("🕵️ AI Investigator is deep-scanning the document..."):
        try:
            # 1. Extract text from PDF
            reader = PdfReader(uploaded_file)
            text = "".join([page.extract_text() for page in reader.pages])
            
            # 2. UPDATED PROMPT FOR HIGHLIGHTING & SUMMARY
            prompt = f"""
            Analyze this document for scams and predatory traps. 
            
            FORMATTING RULES:
            - START with: 'RISK SCORE: [1-10]'
            - HIGHLIGHT the most dangerous parts using Streamlit syntax: :red-background[dangerous text here]
            - HIGHLIGHT important legal terms using: :blue-background[term here]
            - END with a section titled '📝 SUMMARY' that gives a 2-sentence 'Bottom Line'.
            
            STRUCTURE:
            1. Risk Score
            2. 🚩 Red Flags (with highlights)
            3. ⚖️ Legal Loopholes
            4. 💡 Advice
            5. 📝 SUMMARY
            
            Document text: {text[:8000]} 
            """
            
            # 3. GENERATE ANALYSIS
            response = model.generate_content(prompt)
            full_analysis = response.text
            
            # 4. EXTRACT RISK SCORE FOR UI COLORING
            score_match = re.search(r"RISK SCORE:\s*(\d+)", full_analysis)
            score = int(score_match.group(1)) if score_match else 5
            
            st.divider()
            
            # 5. DISPLAY RESULTS WITH COLOR CODING
            if score >= 7:
                st.error(f"### 🚨 HIGH RISK DETECTED (Score: {score}/10)")
            elif score >= 4:
                st.warning(f"### ⚠️ MODERATE RISK (Score: {score}/10)")
            else:
                st.success(f"### ✅ LOW RISK (Score: {score}/10)")
                st.snow()

            # The main report container
            with st.container(border=True):
                st.markdown(full_analysis)
                
        except Exception as e:
            st.error(f"Error during analysis: {e}")

st.divider()
st.caption("Built with 💙 for Legal Safety | 2025")
