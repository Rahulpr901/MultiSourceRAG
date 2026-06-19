# utils/quiz_generator.py

from __future__ import annotations

import os

from google import genai
from dotenv import load_dotenv


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def generate_quiz(
    context: str,
    num_questions: int = 5,
    difficulty: str = "medium",
):
    """
    Generate quiz questions using Gemini.
    """

    prompt = f"""
Generate {num_questions} {difficulty} difficulty MCQ quiz questions.

Use ONLY the provided context.

Context:
{context}

Return format:

Question:
Options:
A.
B.
C.
D.

Correct Answer:
Explanation:
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    return response.text