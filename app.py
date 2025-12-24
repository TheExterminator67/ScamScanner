import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import re

# 1. SETUP
st.set_page_config(page_title="Legal Guard Pro", page_icon="🛡️", layout="wide")

# API KEY CHECK
if "GEMINI_KEY" not in st.secrets:
    st.error("❌ Missing API Key in Secrets!")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_KEY"])
model = genai.GenerativeModel('gemini-3-flash-preview')

# Initialize History for the Chatbox
if "messages" not in st.session_state:
    st.session_state.messages = []

# 2. THE "TRANSLATION THINGY" (Sidebar)
with st.sidebar:
    st.title("🌐 Settings")
    language = st.selectbox(
        "Response Language",
        ["English", "Spanish", "French", "German", "Chinese", "Hindi", "Indonesian"]
    )
    st.divider()
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []

# 3. MAIN SCANNER (The "Like Before" Part)
st.title("🛡️ Legal Guard: :blue[Global Scanner]")
st.write(f"Scanning documents in **{language}**")

uploaded_file = st.file_uploader("Upload a PDF contract", type=["pdf"])

if uploaded_file and st.button("🚀 Start Deep Scan"):
    with st.spinner("🕵️ AI Investigator is reading..."):
        try:
            # Extract PDF Text
            reader = PdfReader(uploaded_file)
            text = "".join([page.extract_text() for page in reader.pages])
            
            # Prompt with Translation & Formatting
            prompt = f"""
            Analyze this document for scams. Respond in {language}.
            FORMATTING: Start with 'RISK SCORE: [1-10]'. 
            Highlight dangerous parts with :red-background[text].
            End with '📝 SUMMARY'.
            Text: {text[:8000]}
            """
            
            response = model.generate_content(prompt)
            full_analysis = response.text
            
            # Score Extraction
            score_match = re.search(r"RISK SCORE:\s*(\d+)", full_analysis)
            score = int(score_match.group(1)) if score_match else 5
            
            # Result Display
            st.divider()
            if score >= 7: st.error(f"### 🚨 HIGH RISK ({score}/10)")
            elif score >= 4: st.warning(f"### ⚠️ MODERATE RISK ({score}/10)")
            else: st.success(f"### ✅ LOW RISK ({score}/10)"); st.snow()
            
            with st.container(border=True):
                st.markdown(full_analysis)
                
        except Exception as e:
            st.error(f"Analysis failed: {e}")

# 4. FLOATING CHATBOX (The "Bottom Corner" Part)
# We use a columns trick or a fixed container to keep it tucked away
with st.sidebar:
    st.write("---")
    with st.popover("💬 Chat with AI", use_container_width=True):
        st.write("Ask follow-up questions about your contract:")
        
        # Display chat history inside the popover
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Chat Input
        if chat_input := st.chat_input("Type a question..."):
            st.session_state.messages.append({"role": "user", "content": chat_input})
            with st.chat_message("user"):
                st.markdown(chat_input)

            # Generate AI Response
            with st.chat_message("assistant"):
                chat_response = model.generate_content(f"User is asking about their contract in {language}: {chat_input}")
                st.markdown(chat_response.text)
                st.session_state.messages.append({"role": "assistant", "content": chat_response.text})

st.caption("Disclaimer: AI analysis, not legal advice.")
