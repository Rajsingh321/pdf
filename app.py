import streamlit as st
import requests
from datetime import datetime

# -----------------------
# Page Configuration
# -----------------------
st.set_page_config(
    page_title="DocuMind",
    page_icon="📚",
    layout="wide"
)

# -----------------------
# Backend Configuration
# -----------------------
API_BASE_URL = "http://localhost:8000"

# -----------------------
# Custom Styling
# -----------------------
st.markdown("""
<style>
.main-title {
    font-size: 2.5rem;
    font-weight: bold;
    color: #1E88E5;
}

.chat-user {
    background-color: #E3F2FD;
    padding: 12px;
    border-radius: 10px;
    margin-bottom: 10px;
}

.chat-assistant {
    background-color: #F5F5F5;
    padding: 12px;
    border-radius: 10px;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------
# Session State
# -----------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "uploaded_docs" not in st.session_state:
    st.session_state.uploaded_docs = []

# -----------------------
# Sidebar
# -----------------------
with st.sidebar:
    st.title("📚 DocuMind")

    st.markdown("---")

    st.subheader("Upload Documents")

    uploaded_files = st.file_uploader(
        "Choose files",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True
    )

    if st.button("Process Documents", use_container_width=True):
        if uploaded_files:
            with st.spinner("Processing documents..."):
                try:
                    files = [
                        ("files", (file.name, file, file.type))
                        for file in uploaded_files
                    ]

                    response = requests.post(
                        f"{API_BASE_URL}/upload",
                        files=files
                    )

                    if response.status_code == 200:
                        st.success("Documents processed successfully!")
                        st.session_state.uploaded_docs = [
                            file.name for file in uploaded_files
                        ]
                    else:
                        st.error("Failed to process documents.")

                except Exception as e:
                    st.error(f"Error: {e}")

    st.markdown("---")

    st.subheader("Uploaded Documents")

    if st.session_state.uploaded_docs:
        for doc in st.session_state.uploaded_docs:
            st.write(f"📄 {doc}")
    else:
        st.info("No documents uploaded yet.")

    st.markdown("---")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# -----------------------
# Main Content
# -----------------------
st.markdown(
    '<p class="main-title">📚 DocuMind</p>',
    unsafe_allow_html=True
)

st.caption("Chat with your documents using AI")

# -----------------------
# Chat History
# -----------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -----------------------
# User Input
# -----------------------
prompt = st.chat_input(
    "Ask a question about your documents..."
)

if prompt:
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/chat",
                    json={
                        "question": prompt,
                        "chat_history": st.session_state.messages
                    }
                )

                if response.status_code == 200:
                    answer = response.json().get(
                        "answer",
                        "No response received."
                    )
                else:
                    answer = "Backend error."

            except Exception as e:
                answer = f"Connection error: {str(e)}"

            st.markdown(answer)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

# -----------------------
# Footer
# -----------------------
st.markdown("---")
st.caption(
    f"DocuMind • Session started {datetime.now().strftime('%d %b %Y')}"
)
