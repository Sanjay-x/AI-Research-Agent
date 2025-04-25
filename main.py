import streamlit as st
import speech_recognition as sr
from google_search import search_google
from scraper import scrape_links
from summarize import summarize_all_from_chromadb
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from io import BytesIO

# API credentials
api_key = "Google API"
search_engine_id = "Search Engine Key"

# recognizer
recognizer = sr.Recognizer()

def recognize_speech():
    with sr.Microphone() as source:
        st.write("🎤 Listening...")
        audio = recognizer.listen(source)
        try:
            query = recognizer.recognize_google(audio)
            st.success(f"You said: {query}")
            return query
        except Exception:
            st.error("Sorry, I couldn't understand. Please try again.")
            return None

# Streamlit UI setup
st.set_page_config(page_title="Research Agent", page_icon="🔍", layout="wide")

# Styling
st.markdown("""
    <style>
        .stApp { background-color: #0d1b2a; color: white; }
        .stButton>button { background-color: #005f73; color: white; }
        .stTextInput>div>input, .stTextArea>div>textarea {
            background-color: #111d2b; color: white; border: 1px solid #005f73;
        }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("Research Agent")
st.subheader("Search, Summarize, and Download Summaries as PDF.")

# Input
query = st.text_input("Enter your query or use voice input")

# Voice Input
if st.button("🎤 Use Voice Input"):
    query = recognize_speech()

# Chat history
if "history" not in st.session_state:
    st.session_state.history = []

# Main logic
if query:
    links = search_google(query, api_key, search_engine_id)
    st.success(f" Found {len(links)} relevant links.")
    if not links:
        st.warning("❌ No results found. Try a different query.")
    else:
        st.session_state.history.append({"role": "user", "text": query})
        scraped_data = scrape_links(links)
        summaries = summarize_all_from_chromadb(query)

        if summaries:
            output = "\n".join([
                f"🔹 **{idx}. {s['title']}**\n🔗 {s['link']}\n📝 {s['summary']}"
                for idx, s in enumerate(summaries, start=1)
            ])
            st.session_state.history.append({"role": "assistant", "text": output})
        else:
            st.warning("❌ No summaries generated.")

# Chat display
for chat in st.session_state.history:
    if chat["role"] == "user":
        st.markdown(f"**You:** {chat['text']}")
    else:
        st.markdown(f"**Agent:** {chat['text']}")

# PDF generator
def generate_pdf(summaries):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    
    title_style = ParagraphStyle(
        name='TitleStyle',
        fontSize=18,
        alignment=1,
        fontName='Helvetica-Bold',
        spaceAfter=12,
        textColor=colors.HexColor('#005f73'),
    )
    link_style = ParagraphStyle(
        name='LinkStyle',
        fontSize=10,
        textColor=colors.blue,
        spaceAfter=4,
    )
    summary_style = ParagraphStyle(
        name='SummaryStyle',
        fontSize=12,
        spaceAfter=10,
        leading=14
    )

    elements = []
    elements.append(Paragraph("Research Summary Report", title_style))
    elements.append(Spacer(1, 20))

    for idx, s in enumerate(summaries, start=1):
        elements.append(Paragraph(f"{idx}. {s['title']}", styles['Heading3']))
        elements.append(Paragraph(f"🔗 <a href='{s['link']}'>{s['link']}</a>", link_style))
        elements.append(Paragraph(s['summary'], summary_style))
        elements.append(Spacer(1, 16))

    doc.build(elements)
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data

# PDF download 
if 'summaries' in locals() and summaries:
    st.markdown("### 📄 Download Summary as PDF")
    pdf_bytes = generate_pdf(summaries)
    st.download_button(
        label="📥 Download PDF",
        data=pdf_bytes,
        file_name="research_summary.pdf",
        mime="application/pdf"
    )
