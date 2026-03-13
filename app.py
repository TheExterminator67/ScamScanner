import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import re

import streamlit as st

# SETUP
st.set_page_config(page_title="Legal Hero", page_icon="🛡️", layout="wide")

if "GEMINI_KEY" not in st.secrets:
    st.error("❌ Missing GEMINI_KEY in Secrets!")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_KEY"])
model = genai.GenerativeModel('gemini-3-flash-preview')

# Initialize History for the Chatbox
if "messages" not in st.session_state:
    st.session_state.messages = []

# SIDEBAR (Translation & Credits)
with st.sidebar:
    st.title("🛡️ Legal Hero")
    
    # Credit in Sidebar
    st.markdown("👨‍💻 **Dev:** Sultan Alnuaimi")
    
    # THE TRANSLATION
    language = st.selectbox(
        "🌐 Select Language",
        ["English", "Arabic", "Spanish", "French", "German", "Chinese", "Hindi", "Indonesian"]
    )
    st.divider()
    st.success("✅ AI Connected")
    if st.button("Clear Chat History"):
        st.session_state.messages = []

# MAIN UI
st.title("🛡️ Legal Hero: Scam Scanner")

uploaded_file = st.file_uploader("Upload a PDF to scan for scams", type=["pdf"])

if uploaded_file:
    if st.button("🕵️ Start Investigation"):
        with st.spinner("AI Investigator is reading the document..."):
            try:
                reader = PdfReader(uploaded_file)
                text = "".join([page.extract_text() for page in reader.pages])
                
                # FORMAT PROMPT
                prompt = f"""
                Analyze this document for scams. Respond entirely in {language}.
                YOU MUST START YOUR RESPONSE WITH: RISK SCORE: [number 1-10]
                Highlight dangerous parts with :red-background[text].
                Include Red Flags, Legal Loopholes, Advice, and a SUMMARY.
                Text: {text[:8000]}
                """
                
                response = model.generate_content(prompt)
                full_analysis = response.text
                
                score_match = re.search(r"RISK SCORE:\s*(\d+)", full_analysis)
                score = int(score_match.group(1)) if score_match else 5
                
                st.divider()
                if score >= 7: st.error(f"### 🚨 HIGH RISK ({score}/10)")
                elif score >= 4: st.warning(f"### ⚠️ MODERATE RISK ({score}/10)")
                else: st.success(f"### ✅ LOW RISK ({score}/10)"); st.snow()
                
                st.markdown(full_analysis)
                    
            except Exception as e:
                st.error(f"Error during analysis: {e}")

# CHATBOT
st.write("---")
col1, col2 = st.columns([8, 2])
with col2:
    with st.popover("💬 Chat with AI"):
        st.markdown(f"**Ask follow-up questions in {language}:**")
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if chat_input := st.chat_input("Ask something..."):
            st.session_state.messages.append({"role": "user", "content": chat_input})
            with st.chat_message("user"): st.markdown(chat_input)

            with st.chat_message("assistant"):
                chat_prompt = f"User is asking about their document in {language}. Document context: {text[:2000] if uploaded_file else 'None'}. Question: {chat_input}"
                chat_res = model.generate_content(chat_prompt)
                st.markdown(chat_res.text)
                st.session_state.messages.append({"role": "assistant", "content": chat_res.text})

# CLEAN AHH FOOTER
st.divider()
st.caption("🛡️ Built by a 16-year-old dev | Disclaimer: AI analysis, not legal advice.")





