import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import re

# 1. SETUP & PAGE CONFIG
st.set_page_config(page_title="Legal Guard Pro", page_icon="🛡️", layout="wide")

# 2. LANGUAGE SELECTOR (The "Translation Thingy")
with st.sidebar:
    st.title("🌐 Settings")
    language = st.selectbox(
        "Select Language / Pilih Bahasa",
        ["English", "Spanish", "French", "German", "Hindi", "Indonesian", "Chinese"]
    )
    st.divider()
    if st.button("Clear Chat History"):
        st.session_state.messages = []

# 3. AI CONFIG
genai.configure(api_key=st.secrets["GEMINI_KEY"])
model = genai.GenerativeModel('gemini-3-flash-preview')

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. MAIN UI
st.title("🛡️ Legal Guard: :blue[Global Scanner]")

uploaded_file = st.file_uploader("Upload a PDF contract", type=["pdf"])

# --- SCANNING LOGIC ---
if uploaded_file and st.button("🚀 Start Deep Scan"):
    with st.spinner("🕵️ Analyzing..."):
        reader = PdfReader(uploaded_file)
        text = "".join([page.extract_text() for page in reader.pages])
        
        # We tell the AI to translate the entire report into the chosen language
        prompt = f"""
        Analyze this document for scams.
        LANGUAGE: {language}
        RULES: Start with 'RISK SCORE: [1-10]'. Use colors and emojis.
        End with a '📝 SUMMARY'.
        Text: {text[:8000]}
        """
        response = model.generate_content(prompt)
        
        # Save to chat history
        st.session_state.messages.append({"role": "assistant", "content": response.text})

# --- 5. THE CHATBOX (Highkey Feature) ---
st.divider()
st.subheader("💬 Chat with your AI Investigator")

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if chat_input := st.chat_input("Ask a follow-up question about the contract..."):
    # Display user message in chat message container
    st.chat_message("user").markdown(chat_input)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": chat_input})

    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            chat_prompt = f"The user is asking about the previous contract in {language}: {chat_input}"
            response = model.generate_content(chat_prompt)
            st.markdown(response.text)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response.text})
