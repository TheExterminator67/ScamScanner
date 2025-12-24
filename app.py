import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import re

# --- 1. SETUP ---
st.set_page_config(page_title="Legal Guard", page_icon="🛡️", layout="wide")

# API KEY CHECK
if "GEMINI_KEY" not in st.secrets:
    st.error("❌ Missing GEMINI_KEY in Secrets!")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_KEY"])
model = genai.GenerativeModel('gemini-3-flash-preview')

# Initialize History for the Chatbox
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 2. SIDEBAR (Translation & Status) ---
with st.sidebar:
    st.title("🛡️ Legal Guard")
    # THE TRANSLATION THINGY
    language = st.selectbox(
        "🌐 Select Language",
        ["English", "Spanish", "French", "German", "Chinese", "Hindi", "Indonesian"]
    )
    st.divider()
    st.success("✅ AI Brain Connected")
    if st.button("Clear Chat"):
        st.session_state.messages = []

# --- 3. MAIN UI (Like Before) ---
st.title("🛡️ Legal Guard: Scam Scanner")

uploaded_file = st.file_uploader("Upload a PDF to scan for scams", type=["pdf"])

if uploaded_file:
    if st.button("🕵️ Start Investigation"):
        with st.spinner("AI Investigator is reading the document..."):
            try:
                # Extract text from PDF
                reader = PdfReader(uploaded_file)
                text = "".join([page.extract_text() for page in reader.pages])
                
                # FORMAT PROMPT (Updated for Translation)
                prompt = f"""
                Analyze this document for scams. Respond in {language}.
                YOU MUST START YOUR RESPONSE WITH THIS EXACT LINE:
                RISK SCORE: [number 1-10]
                
                Then, provide a detailed report including:
                - 🚩 Red Flags (Highlight dangerous parts with :red-background[text])
                - ⚖️ Legal Loopholes
                - 💡 Advice
                - 📝 SUMMARY (at the end)
                
                Document text: {text[:8000]}
                """
                
                response = model.generate_content(prompt)
                full_analysis = response.text
                
                # EXTRACT RISK SCORE
                score_match = re.search(r"RISK SCORE:\s*(\d+)", full_analysis)
                score = int(score_match.group(1)) if score_match else 5
                
                st.divider()
                
                # DISPLAY BASED ON RISK LEVEL
                if score >= 7:
                    st.error(f"### 🚨 HIGH RISK (Score: {score}/10)")
                    st.markdown(full_analysis)
                elif score >= 4:
                    st.warning(f"### ⚠️ MODERATE RISK (Score: {score}/10)")
                    st.markdown(full_analysis)
                else:
                    st.success(f"### ✅ LOW RISK (Score: {score}/10)")
                    st.markdown(full_analysis)
                    st.snow()
                    
            except Exception as e:
                st.error(f"Error during analysis: {e}")

# --- 4. FLOATING CHATBOX (Bottom Right Corner Effect) ---
# We use columns to push the popover to the far right
st.write("---")
col1, col2 = st.columns([8, 2])
with col2:
    with st.popover("💬 Chat with AI"):
        st.markdown(f"**Ask follow-up questions in {language}:**")
        
        # Display chat history
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Chat Input
        if chat_input := st.chat_input("Ask something..."):
            st.session_state.messages.append({"role": "user", "content": chat_input})
            with st.chat_message("user"):
                st.markdown(chat_input)

            # Generate AI Response
            with st.chat_message("assistant"):
                chat_prompt = f"User is asking about their document in {language}. Document context: {text[:2000] if uploaded_file else 'None'}. Question: {chat_input}"
                chat_res = model.generate_content(chat_prompt)
                st.markdown(chat_res.text)
                st.session_state.messages.append({"role": "assistant", "content": chat_res.text})

st.caption("Disclaimer: This is an AI tool, not a lawyer.")
