# app.py

from __future__ import annotations

import os

os.makedirs("uploads", exist_ok=True)
os.makedirs("data/faiss_index", exist_ok=True)

import streamlit as st

from utils.pdf_processor import extract_pdf_pages
from utils.youtube_processor import get_youtube_transcript
from utils.chunker import (
    chunk_pdf_pages,
    chunk_youtube_transcript,
)
from utils.vector_store import FAISSVectorStore
from utils.rag_pipeline import ask_question
from utils.quiz_generator import generate_quiz


st.set_page_config(
    page_title="Multi-Source RAG Learning",
    layout="wide",
)

st.title("📚 Multi-Source Learning Assistant")


vector_store = FAISSVectorStore()


INDEX_PATH = "data/faiss_index/faiss.index"
METADATA_PATH = "data/faiss_index/metadata.pkl"


if os.path.exists(INDEX_PATH):
    vector_store.load(INDEX_PATH, METADATA_PATH)


st.sidebar.header("Upload Sources")


uploaded_pdfs = st.sidebar.file_uploader(
    "Upload PDFs",
    type=["pdf"],
    accept_multiple_files=True,
)


youtube_links = st.sidebar.text_area(
    "Paste YouTube Links (one per line)"
)


if st.sidebar.button("Process Content"):

    all_chunks = []

    # PDF PROCESSING
    if uploaded_pdfs:

        for uploaded_pdf in uploaded_pdfs:

            pdf_path = os.path.join(
                "uploads",
                uploaded_pdf.name,
            )

            with open(pdf_path, "wb") as f:
                f.write(uploaded_pdf.getbuffer())

            pages_data = extract_pdf_pages(pdf_path)

            pdf_chunks = chunk_pdf_pages(pages_data)

            all_chunks.extend(pdf_chunks)

    # YOUTUBE PROCESSING
    if youtube_links:

        links = youtube_links.strip().split("\n")

        for link in links:

            transcript_data = get_youtube_transcript(link)

            yt_chunks = chunk_youtube_transcript(
                transcript_data
            )

            all_chunks.extend(yt_chunks)

    # ADD TO FAISS
    if all_chunks:

        vector_store.add_documents(all_chunks)

        vector_store.save(
            INDEX_PATH,
            METADATA_PATH,
        )

        st.success("Content processed successfully!")

    else:
        st.warning("No content found.")


st.header("❓ Ask Questions")

user_question = st.text_input(
    "Ask anything from uploaded content"
)


if st.button("Get Answer"):

    if user_question:

        result = ask_question(vector_store, user_question)

        st.subheader("Answer")

        st.write(result["answer"])

        st.subheader("Sources")

        for source in result["sources"]:

            if "page_number" in source:
                st.write(
                    f"📄 {source['source']} "
                    f"(Page {source['page_number']})"
                )

            elif "timestamp" in source:
                st.write(
                    f"📺 {source['source']} "
                    f"({source['timestamp']})"
                )


st.header("🧠 Quiz Generator")

num_questions = st.slider(
    "Number of Questions",
    1,
    20,
    5,
)

difficulty = st.selectbox(
    "Difficulty",
    ["easy", "medium", "hard"],
)


if st.button("Generate Quiz"):

    all_content = ""

    for item in vector_store.metadata_store:
        all_content += item["content"] + "\n"

    quiz = generate_quiz(
        context=all_content,
        num_questions=num_questions,
        difficulty=difficulty,
    )

    st.subheader("Generated Quiz")

    st.write(quiz)