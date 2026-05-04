from groq import Groq
from openai import OpenAI
import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

if not OPENROUTER_API_KEY:
    raise ValueError(" OPENROUTER_API_KEY not found in .env file!")

def question_to_cypher(question):
    """
    Final unified Cypher generator for SBC Neo4j graph.
    Covers all major question types.
    """

    prompt = f"""
You are an expert Neo4j Cypher query generator for health insurance SBC documents.

-------------------------------
GRAPH SCHEMA
-------------------------------
- Nodes: (:Entity)
- Properties:
  name (mandatory), value, answer, network_cost, out_of_network_cost, limitations, medical_event
- Relationships:
  HAS_COPAY, HAS_COINSURANCE, LIMITATIONS, NOT_COVERED, COVERS,
  REQUIRES, NETWORK_COST, OUT_OF_NETWORK_COST, DEDUCTIBLE,
  REDUCES_BENEFIT, APPLIES_TO

-------------------------------
STRICT RULES (MUST FOLLOW)
-------------------------------
1. Return ONLY Cypher query (no explanation, no markdown).
2. Always use case-insensitive matching:
   toLower(e.name) CONTAINS "<keyword>"
3. Prefer OPTIONAL MATCH if relationship is unclear.
4. Always return:
   e.name AS entity,
   type(r) AS relationship,
   result

5. Always use:
   coalesce(e.answer, e.value, e.network_cost, e.out_of_network_cost, v.name)
6. Use correct relationship types when question implies it.
7. Always include ORDER BY relationship
8. If the question asks about "other covered services" or similar,
   you MUST use the relationship :OTHER_SERVICES
   and NOT the generic query pattern.
9. DO NOT use `toLower(e.name) CONTAINS "<keyword>"` 
   when the question refers to a SECTION (like other covered services, excluded services, etc.)
10. USE Examples as reference.


-------------------------------
SMART QUERY PATTERN
-------------------------------
MATCH (e:Entity)
WHERE toLower(e.name) CONTAINS "<keyword>"
OPTIONAL MATCH (e)-[r]-(v)

RETURN 
    e.name AS entity,
    type(r) AS relationship,
    coalesce(
        e.answer,
        e.value,
        e.network_cost,
        e.out_of_network_cost,
        e.limitations,
        v.name,
        v.value,
        e.why_it_matters
    ) AS result
ORDER BY relationship

-------------------------------
SPECIALIZED PATTERNS
-------------------------------
# Important Questions
MATCH (p:Entity)-[:HAS_IMPORTANT_QUESTION]->(iq:Entity)
OPTIONAL MATCH (iq)-[r]-(v)
RETURN
iq.name AS important_question,
iq.answer AS answer,
iq.why_it_matters AS why_it_matters,
type(r) AS relationship,
coalesce(v.name, iq.value) AS extra_info
ORDER BY iq.name

# Copay
MATCH (e:Entity)-[r:HAS_COPAY]->(v)
WHERE toLower(e.name) CONTAINS "<keyword>"
RETURN e.name AS entity, type(r) AS relationship, v.name AS result
ORDER BY relationship

# Coinsurance
MATCH (e:Entity)-[r:HAS_COINSURANCE]->(v)
WHERE toLower(e.name) CONTAINS "<keyword>"
RETURN e.name AS entity, type(r) AS relationship, v.name AS result
ORDER BY relationship

# Other Covered Services
MATCH (e:Entity)-[r:OTHER_SERVICES]->(v)
RETURN e.name AS entity, type(r) AS relationship, v.name AS result
ORDER BY result

RETURN e.name AS entity

# General Cost/Limit
MATCH (e:Entity)
WHERE toLower(e.name) CONTAINS "<keyword>"
OPTIONAL MATCH (e)-[r]->(v)
RETURN 
    e.name AS entity,
    type(r) AS relationship,
    coalesce(e.network_cost, e.out_of_network_cost, e.limitations, v.name) AS result
ORDER BY relationship

# Not Covered
MATCH (e:Entity)-[r:NOT_COVERED]->(v)
RETURN e.name AS entity, type(r) AS relationship, v.name AS result
ORDER BY result


# Requires (Preauthorization etc.)
MATCH (e:Entity)-[r:REQUIRES]->(v)
WHERE toLower(e.name) CONTAINS "<keyword>"
RETURN e.name AS entity, type(r) AS relationship, v.name AS result

# Network Cost
MATCH (e:Entity)-[r:NETWORK_COST]->(v)
WHERE toLower(e.name) CONTAINS "<keyword>"
RETURN e.name AS entity, type(r) AS relationship, v.name AS result

# Out of Network Cost
MATCH (e:Entity)-[r:OUT_OF_NETWORK_COST]->(v)
WHERE toLower(e.name) CONTAINS "<keyword>"
RETURN e.name AS entity, type(r) AS relationship, v.name AS result

# Deductible
MATCH (e:Entity)
WHERE toLower(e.name) CONTAINS "deductible"
OPTIONAL MATCH (e)-[r]-(v)
RETURN 
    e.name AS entity,
    type(r) AS relationship,
    coalesce(e.value, v.name, e.network_cost, e.answer) AS result
ORDER BY relationship

# Out-of-pocket limit
MATCH (e:Entity)
WHERE toLower(e.name) CONTAINS "out-of-pocket limit"
   OR toLower(e.name) CONTAINS "oop limit"
OPTIONAL MATCH (e)-[r]-(v)
RETURN 
    e.name AS entity,
    type(r) AS relationship,
    coalesce(e.answer, e.value, e.network_cost, e.out_of_network_cost, v.name) AS result
ORDER BY relationship


EXAMPLES:

Q: What are other covered services?
A:
MATCH (:Entity)-[r:OTHER_SERVICES]->(v)
RETURN 
    "Other Covered Services" AS entity,
    type(r) AS relationship,
    v.name AS result
ORDER BY result

Q: Are there services covered before you meet your deductible?
A:
MATCH (e:Entity)-[r:ANSWER]->(v:Value)
WHERE toLower(q.name) CONTAINS "before deductibles"
   OR toLower(q.name) CONTAINS "services covered"

RETURN 
    v.name AS answer

Q: Are there other deductibles for specific services?
A:
MATCH (e:Entity)-[r:ANSWER]->(v:Value)
WHERE toLower(e.name) CONTAINS "other deductibles"
   OR toLower(e.name) CONTAINS "specific services"

RETURN 
    v.name AS answer


Q: What is the copayment for preferred brand drugs?
A:
MATCH (e:Entity)-[r]->(v:Value)
WHERE toLower(e.name) CONTAINS "preferred brand drugs"
AND type(r) IN ["COPAY", "COPAYMENT"]
RETURN e.name, type(r), v.name

Q: What is not included in the out-of-pocket limit?
A: 
MATCH (q:Entity)-[:ANSWER]->(v:Value)
WHERE toLower(q.name) CONTAINS "not included in the out-of-pocket limit"
RETURN 
    q.name AS entity,
    "ANSWER" AS relationship,
    v.name AS result

Q: What is the cost of prescription?
A:
MATCH (e:Entity)-[r]->(v:Value)
WHERE toLower(e.name) CONTAINS "prescription"
AND type(r) = "COST"
RETURN e.name, type(r), v.name

Q: What are the limitations of generic drugs?
A:
MATCH (e:Entity)-[:LIMITATIONS]->(v:Value)
WHERE toLower(e.name) CONTAINS "generic drugs"
RETURN v.name AS limitations

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

-------------------------------
QUESTION:
{question}
"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "http://localhost",
        "X-Title": "SBC Cypher Generator",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "meta-llama/llama-4-maverick",   # This one is reliable
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "max_tokens": 800
    }

    try:
        response = requests.post(
            OPENROUTER_API_URL,
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code != 200:
            print(f"OpenRouter Error {response.status_code}: {response.text}")
            raise Exception(f"Status {response.status_code}")

        result = response.json()
        cypher = result['choices'][0]['message']['content'].strip()

        # Clean code blocks
        cypher = re.sub(r"```(?:cypher)?\s*", "", cypher)
        cypher = re.sub(r"```\s*$", "", cypher)

        return cypher.strip()

    except Exception as e:
        print(f" Cypher generation failed: {e}")
        # Safe fallback for deductible questions
        return """
MATCH (e:Entity)
WHERE toLower(e.name) CONTAINS "deductible" 
   OR toLower(e.name) CONTAINS "overall deductible"
OPTIONAL MATCH (e)-[r]-(v)
RETURN 
    e.name AS entity,
    type(r) AS relationship,
    coalesce(e.answer, e.value, e.network_cost, v.name) AS result
ORDER BY relationship
"""

