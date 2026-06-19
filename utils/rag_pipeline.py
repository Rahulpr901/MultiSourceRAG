# utils/rag_pipeline.py

from __future__ import annotations

import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def build_context(search_results):
    """
    Convert retrieved chunks into prompt context.
    """
    context = ""

    for idx, result in enumerate(search_results, start=1):
        source_info = ""

        if "page_number" in result:
            source_info = f"PDF: {result['source']} | Page: {result['page_number']}"
        elif "timestamp" in result:
            source_info = f"YouTube: {result['source']} | Timestamp: {result['timestamp']}"

        context += (
            f"\n\nSource {idx}:\n"
            f"{source_info}\n"
            f"{result['content']}"
        )

    return context


def ask_question(vector_store, query: str, top_k: int = 5):
    """
    RAG-based question answering.
    """
    retrieved_docs = vector_store.search(query, top_k=top_k)

    if not retrieved_docs:
        return {
            "answer": "I could not find relevant content in the uploaded sources.",
            "sources": []
        }

    context = build_context(retrieved_docs)

    prompt = f"""
You are an AI study assistant.

Answer the user's question ONLY from the provided context.

If the answer is not present, say:
"I could not find the answer in the uploaded content."

Context:
{context}

Question:
{query}

Provide:
1. Clear answer
2. Source references
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    return {
        "answer": response.text,
        "sources": retrieved_docs,
    }