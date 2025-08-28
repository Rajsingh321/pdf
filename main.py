import streamlit as st
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq

st.set_page_config(page_title="📄 PDF Q&A Agent", page_icon="🤖")
st.title("📄 Ask Questions from your PDF with AI")

uploaded_file = st.file_uploader("Upload your PDF file", type=["pdf"])

if uploaded_file:
    with open("uploaded.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success("✅ PDF uploaded successfully!")

    loader = PyPDFLoader("uploaded.pdf")
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=200)
    chunks = splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db = Chroma.from_documents(chunks, embedding=embeddings)
    retriever = db.as_retriever(search_kwargs={"k": 4})

    llm = ChatGroq(
        groq_api_key=os.environ["GROQ_API_KEY"],
        model="llama-3.1-8b-instant",
        temperature=0,
        max_tokens=512
    )

    st.subheader("🔎 Ask a Question about the PDF")
    query = st.text_input("Enter your question:")

    if query:
        docs = retriever.get_relevant_documents(query)
        context = " ".join([doc.page_content for doc in docs])

        prompt = f"""
        You are a helpful assistant. 
        Question: {query}
        Context: {context}
        Answer shortly and clearly:
        """

        with st.spinner("Thinking..."):
            response = llm.invoke(prompt)

        st.success("✅ Answer:")
        st.write(response.content.strip())