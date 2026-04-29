# src/query_to_cypher.py
from groq import Groq
import os
from dotenv import load_dotenv
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def question_to_cypher(question):
    """
    Improved Cypher generator specialized for SBC (Summary of Benefits and Coverage) documents.
    """
    prompt = f"""
You are an expert Neo4j Cypher query generator for health insurance Summary of Benefits and Coverage (SBC) documents.

### Graph Schema:
- All nodes have label `:Entity`
- Every node has a `name` property (very important)
- Some nodes also have properties like: `network_cost`, `out_of_network_cost`, `answer`, `value`, `limitations`, `medical_event`
- Relationships connect entities with various types (EXCLUDES, OFFERS, HAS_ANSWER, etc.)

### STRICT INSTRUCTIONS:
- Return **ONLY** valid Cypher code. No explanations, no markdown, no extra text.
- Use `toLower(e.name)` for case-insensitive matching.
- Prefer `OPTIONAL MATCH` to avoid empty results.
- Use `coalesce()` to return the most useful value (network_cost, answer, value, name).
- Always include at least: entity name, relationship type, and value/result.

### Good Query Patterns:

1. For "Out-of-Pocket Limit" questions:
```cypher
MATCH (e:Entity)
WHERE toLower(e.name) CONTAINS "out-of-pocket limit" OR toLower(e.name) CONTAINS "oop limit"
OPTIONAL MATCH (e)-[r]-(v)
RETURN e.name AS entity,
       type(r) AS relationship,
       coalesce(e.answer, e.value, v.name, e.network_cost) AS result
ORDER BY type(r)

---

EXAMPLES:

Q: What is the copayment for preferred brand drugs?
A:
MATCH (e:Entity)-[r]->(v:Value)
WHERE toLower(e.name) CONTAINS "preferred brand drugs"
AND type(r) IN ["COPAY", "COPAYMENT"]
RETURN e.name, type(r), v.name

Q: What is the cost of prescription?
A:
MATCH (e:Entity)-[r]->(v:Value)
WHERE toLower(e.name) CONTAINS "prescription"
AND type(r) = "COST"
RETURN e.name, type(r), v.name

Q: What is the deductible?
A: MATCH (e:Entity)
WHERE toLower(e.name) CONTAINS "deductible"

OPTIONAL MATCH (e)-[r]-(v)
RETURN
    e.name AS deductible_type,
    type(r) AS relationship,
    coalesce( e.value, v.name, e.network_cost) AS deductible_info,
    e.answer AS full_answer
ORDER BY type(r)


---

QUESTION:
{question}
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
         stop=["\n\n"]
    )
    return response.choices[0].message.content.strip()


