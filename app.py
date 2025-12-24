import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# page config
st.set_page_config(page_title="Legal Guard", page_icon="🛡️")

# setup
if "GEMINI_KEY" not in st.secrets:
    st.error("❌ GEMINI_KEY missing! Go to Streamlit Settings > Secrets and add it.")
    st.stop()


genai.configure(api_key=st.secrets["GEMINI_KEY"])

# Initialize the Model GLOBALLY
# Using the '-latest' suffix fixes the 404/v1beta mismatch
model = genai.GenerativeModel('gemini-1.5-flash-latest')

# PDF Helper Function
def get_pdf_text(upload):
    pdf = PdfReader(upload)
    content = ""
    for page in pdf.pages:
        content += page.extract_text()
    return content

# ui
st.title("🛡️ Legal Guard: AI Scam Scanner")
st.write("I help you find hidden traps in contracts. Upload your PDF below.")

file = st.file_uploader("Upload Contract (PDF)", type="pdf")

if st.button("Analyze Document"):
    if file:
        with st.spinner("Scanning for red flags..."):
            try:
                # Turn PDF into text
                text_content = get_pdf_text(file)
                
                # Ask Gemini to scan it
                prompt = f"Analyze this contract for scams, predatory language, or hidden fees: {text_content[:8000]}"
                response = model.generate_content(prompt)
                
                # Show results
                st.subheader("Analysis Results")
                st.write(response.text)
                st.success("Done!")
            except Exception as e:
                st.error(f"Analysis failed: {e}")
    else:
        st.warning("Please upload a file first!")

st.divider()
st.caption("Built by a 16-year-old dev | 2025 AI Safety Project")




