import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import re

# SETUP
API_KEY = "AIzaSyAdLkKKdi7DebShLbwgN6cpKVaX1OKhY6w" 
genai.configure(api_key=API_KEY)

# GEMINI MODEL
model_names = ['gemini-3-flash', 'gemini-2.5-flash', 'gemini-1.5-flash']
model = None
for name in model_names:
    try:
        test_model = genai.GenerativeModel(name)
        test_model.generate_content("test", generation_config={"max_output_tokens": 1})
        model = test_model
        break 
    except: continue

# UI
st.set_page_config(page_title="Legal Guard", page_icon="🛡️")
st.title("🛡️ Legal Guard: Scam Scanner")

uploaded_file = st.file_uploader("Upload a PDF to scan for scams", type=["pdf"])

if uploaded_file:
    with st.spinner("🕵️ AI Investigator is reading the document..."):
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
        
        Document text: {text}
        """
        
        try:
            response = model.generate_content(prompt)
            full_analysis = response.text
            
            # COLOR-CODED OUTPUT BASED ON RISK SCORE
            # EXTRACT RISK SCORE
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
            st.error(f"Error during analysis: {e}")

st.caption("Disclaimer: This is an AI tool, not a lawyer. Always read the fine print!")