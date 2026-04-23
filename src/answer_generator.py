# src/answer_generator.py
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_answer(question, db_result):
    prompt = f"""
    You are answering a user question using ONLY Neo4j database results.

    Your job is to convert structured database output into a clear answer.

    STRICT RULES:

    1. ONLY use the provided database results
    2. DO NOT add any external knowledge
    3. DO NOT guess or hallucinate
    4. If database results are EMPTY or insufficient:
    respond exactly:
    "No relevant information found in the database."

    5. Interpret graph structure:
    - e.name = entity
    - type(r) = relationship
    - v.name = value

    6. Convert relationships into natural language:
    Example:
    ("Primary care visit", "HAS_NETWORK_COST", "$35 copay")
    → "The network cost of primary care visit is $35 copay."

    7. If multiple results exist:
    - Combine them clearly
    - Group similar information

    8. Keep answer concise and factual

    OUTPUT:
    Return only the final answer (no explanation).

    Schema:
    (Entity)-[RELATION]->(Entity/Value)

    User Question:
    {question}
    DATABASE RESULTS:
    {db_result}

    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content.strip()
