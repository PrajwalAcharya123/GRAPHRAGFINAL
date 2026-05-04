# from groq import Groq
# from openai import OpenAI
# import os
# import re
# import requests
# from dotenv import load_dotenv

# load_dotenv()

# OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
# OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# if not OPENROUTER_API_KEY:
#     raise ValueError(" OPENROUTER_API_KEY not found in .env file!")

# def question_to_cypher(question):
#     """
#     Final unified Cypher generator for SBC Neo4j graph.
#     Covers all major question types.
#     """

#     prompt = f"""
# You are an expert Neo4j Cypher query generator for health insurance SBC documents.

# -------------------------------
# GRAPH SCHEMA
# -------------------------------
# - Nodes: (:Entity)
# - Properties:
#   name (mandatory), value, answer, network_cost, out_of_network_cost, limitations, medical_event
# - Relationships:
#   HAS_COPAY, HAS_COINSURANCE, LIMITATIONS, NOT_COVERED, COVERS,
#   REQUIRES, NETWORK_COST, OUT_OF_NETWORK_COST, DEDUCTIBLE,
#   REDUCES_BENEFIT, APPLIES_TO

# -------------------------------
# STRICT RULES (MUST FOLLOW)
# -------------------------------
# 1. Return ONLY Cypher query (no explanation, no markdown).
# 2. Always use case-insensitive matching:
#    toLower(e.name) CONTAINS "<keyword>"
# 3. Prefer OPTIONAL MATCH if relationship is unclear.
# 4. Always return:
#    e.name AS entity,
#    type(r) AS relationship,
#    result

# 5. Always use:
#    coalesce(e.answer, e.value, e.network_cost, e.out_of_network_cost, v.name)
# 6. Use correct relationship types when question implies it.
# 7. Always include ORDER BY relationship
# 8. If the question asks about "other covered services" or similar,
#    you MUST use the relationship :OTHER_SERVICES
#    and NOT the generic query pattern.
# 9. DO NOT use `toLower(e.name) CONTAINS "<keyword>"` 
#    when the question refers to a SECTION (like other covered services, excluded services, etc.)
# 10. USE Examples as reference.


# -------------------------------
# SMART QUERY PATTERN
# -------------------------------
# MATCH (e:Entity)
# WHERE toLower(e.name) CONTAINS "<keyword>"
# OPTIONAL MATCH (e)-[r]-(v)

# RETURN 
#     e.name AS entity,
#     type(r) AS relationship,
#     coalesce(
#         e.answer,
#         e.value,
#         e.network_cost,
#         e.out_of_network_cost,
#         e.limitations,
#         v.name,
#         v.value,
#         e.why_it_matters
#     ) AS result
# ORDER BY relationship

# -------------------------------
# SPECIALIZED PATTERNS
# -------------------------------
# # Important Questions
# MATCH (p:Entity)-[:HAS_IMPORTANT_QUESTION]->(iq:Entity)
# OPTIONAL MATCH (iq)-[r]-(v)
# RETURN
# iq.name AS important_question,
# iq.answer AS answer,
# iq.why_it_matters AS why_it_matters,
# type(r) AS relationship,
# coalesce(v.name, iq.value) AS extra_info
# ORDER BY iq.name

# # Copay
# MATCH (e:Entity)-[r:HAS_COPAY]->(v)
# WHERE toLower(e.name) CONTAINS "<keyword>"
# RETURN e.name AS entity, type(r) AS relationship, v.name AS result
# ORDER BY relationship

# # Coinsurance
# MATCH (e:Entity)-[r:HAS_COINSURANCE]->(v)
# WHERE toLower(e.name) CONTAINS "<keyword>"
# RETURN e.name AS entity, type(r) AS relationship, v.name AS result
# ORDER BY relationship

# # Other Covered Services
# MATCH (e:Entity)-[r:OTHER_SERVICES]->(v)
# RETURN e.name AS entity, type(r) AS relationship, v.name AS result
# ORDER BY result

# RETURN e.name AS entity

# # General Cost/Limit
# MATCH (e:Entity)
# WHERE toLower(e.name) CONTAINS "<keyword>"
# OPTIONAL MATCH (e)-[r]->(v)
# RETURN 
#     e.name AS entity,
#     type(r) AS relationship,
#     coalesce(e.network_cost, e.out_of_network_cost, e.limitations, v.name) AS result
# ORDER BY relationship

# # Not Covered
# MATCH (e:Entity)-[r:NOT_COVERED]->(v)
# RETURN e.name AS entity, type(r) AS relationship, v.name AS result
# ORDER BY result


# # Requires (Preauthorization etc.)
# MATCH (e:Entity)-[r:REQUIRES]->(v)
# WHERE toLower(e.name) CONTAINS "<keyword>"
# RETURN e.name AS entity, type(r) AS relationship, v.name AS result

# # Network Cost
# MATCH (e:Entity)-[r:NETWORK_COST]->(v)
# WHERE toLower(e.name) CONTAINS "<keyword>"
# RETURN e.name AS entity, type(r) AS relationship, v.name AS result

# # Out of Network Cost
# MATCH (e:Entity)-[r:OUT_OF_NETWORK_COST]->(v)
# WHERE toLower(e.name) CONTAINS "<keyword>"
# RETURN e.name AS entity, type(r) AS relationship, v.name AS result

# # Deductible
# MATCH (e:Entity)
# WHERE toLower(e.name) CONTAINS "deductible"
# OPTIONAL MATCH (e)-[r]-(v)
# RETURN 
#     e.name AS entity,
#     type(r) AS relationship,
#     coalesce(e.value, v.name, e.network_cost, e.answer) AS result
# ORDER BY relationship

# # Out-of-pocket limit
# MATCH (e:Entity)
# WHERE toLower(e.name) CONTAINS "out-of-pocket limit"
#    OR toLower(e.name) CONTAINS "oop limit"
# OPTIONAL MATCH (e)-[r]-(v)
# RETURN 
#     e.name AS entity,
#     type(r) AS relationship,
#     coalesce(e.answer, e.value, e.network_cost, e.out_of_network_cost, v.name) AS result
# ORDER BY relationship


# EXAMPLES:

# Q: What are other covered services?
# A:
# MATCH (:Entity)-[r:OTHER_SERVICES]->(v)
# RETURN 
#     "Other Covered Services" AS entity,
#     type(r) AS relationship,
#     v.name AS result
# ORDER BY result

# Q: Are there services covered before you meet your deductible?
# A:
# MATCH (e:Entity)-[r:ANSWER]->(v:Value)
# WHERE toLower(q.name) CONTAINS "before deductibles"
#    OR toLower(q.name) CONTAINS "services covered"

# RETURN 
#     v.name AS answer

# Q: Are there other deductibles for specific services?
# A:
# MATCH (e:Entity)-[r:ANSWER]->(v:Value)
# WHERE toLower(e.name) CONTAINS "other deductibles"
#    OR toLower(e.name) CONTAINS "specific services"

# RETURN 
#     v.name AS answer


# Q: What is the copayment for preferred brand drugs?
# A:
# MATCH (e:Entity)-[r]->(v:Value)
# WHERE toLower(e.name) CONTAINS "preferred brand drugs"
# AND type(r) IN ["COPAY", "COPAYMENT"]
# RETURN e.name, type(r), v.name

# Q: What is not included in the out-of-pocket limit?
# A: 
# MATCH (q:Entity)-[:ANSWER]->(v:Value)
# WHERE toLower(q.name) CONTAINS "not included in the out-of-pocket limit"
# RETURN 
#     q.name AS entity,
#     "ANSWER" AS relationship,
#     v.name AS result

# Q: What is the cost of prescription?
# A:
# MATCH (e:Entity)-[r]->(v:Value)
# WHERE toLower(e.name) CONTAINS "prescription"
# AND type(r) = "COST"
# RETURN e.name, type(r), v.name

# Q: What are the limitations of generic drugs?
# A:
# MATCH (e:Entity)-[:LIMITATIONS]->(v:Value)
# WHERE toLower(e.name) CONTAINS "generic drugs"
# RETURN v.name AS limitations

# Q: What is the deductible?
# A: MATCH (e:Entity)
# WHERE toLower(e.name) CONTAINS "deductible"

# OPTIONAL MATCH (e)-[r]-(v)
# RETURN
#     e.name AS deductible_type,
#     type(r) AS relationship,
#     coalesce( e.value, v.name, e.network_cost) AS deductible_info,
#     e.answer AS full_answer
# ORDER BY type(r)

# -------------------------------
# QUESTION:
# {question}
# """

#     headers = {
#         "Authorization": f"Bearer {OPENROUTER_API_KEY}",
#         "HTTP-Referer": "http://localhost",
#         "X-Title": "SBC Cypher Generator",
#         "Content-Type": "application/json"
#     }

#     payload = {
#         "model": "meta-llama/llama-4-maverick",   # This one is reliable
#         "messages": [{"role": "user", "content": prompt}],
#         "temperature": 0.0,
#         "max_tokens": 800
#     }

#     try:
#         response = requests.post(
#             OPENROUTER_API_URL,
#             headers=headers,
#             json=payload,
#             timeout=60
#         )
        
#         if response.status_code != 200:
#             print(f"OpenRouter Error {response.status_code}: {response.text}")
#             raise Exception(f"Status {response.status_code}")

#         result = response.json()
#         cypher = result['choices'][0]['message']['content'].strip()

#         # Clean code blocks
#         cypher = re.sub(r"```(?:cypher)?\s*", "", cypher)
#         cypher = re.sub(r"```\s*$", "", cypher)

#         return cypher.strip()

#     except Exception as e:
#         print(f" Cypher generation failed: {e}")
#         # Safe fallback for deductible questions
#         return """
# MATCH (e:Entity)
# WHERE toLower(e.name) CONTAINS "deductible" 
#    OR toLower(e.name) CONTAINS "overall deductible"
# OPTIONAL MATCH (e)-[r]-(v)
# RETURN 
#     e.name AS entity,
#     type(r) AS relationship,
#     coalesce(e.answer, e.value, e.network_cost, v.name) AS result
# ORDER BY relationship
# """
from openai import OpenAI
import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found in .env file!")


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
    name (main identifier)
    value (for copay/coinsurance)
    raw (full cost string)
    text (limitations)
----------------------------------
GRAPH RELATIONSHIPS
----------------------------------
Service → HAS_NETWORK_COST → costNode
Service → HAS_OUT_OF_NETWORK_COST → costNode

costNode → HAS_COPAY → detailNode
costNode → HAS_COINSURANCE → detailNode

Service → HAS_LIMITATION → limitationNode
Service → REQUIRES → Preauthorization


-------------------------------
STRICT RULES (MUST FOLLOW)
-------------------------------
1. Output ONLY Cypher (no explanation).
2. ALWAYS use case-insensitive search:
   toLower(s.name) CONTAINS toLower("<keyword>")
3. ALWAYS traverse BOTH:
   HAS_NETWORK_COST and HAS_OUT_OF_NETWORK_COST
4. VALUE is a REQUIRED final hop:
   detailNode NEVER contains the actual value.
   You MUST ALWAYS use:

   OPTIONAL MATCH (detailNode)-[:VALUE]->(valNode)

   and return valNode.value
5. Use properties:
   - detailNode.value
   - costNode.raw
   - rawNode.value
   - limitationNode.text
6. Prefer OPTIONAL MATCH
7. Always return:
   entity, relationship, result
8. Use exact EXAMPLES template, if question matches 

-------------------------------
SMART QUERY PATTERN
-------------------------------
MATCH (s:Entity)
WHERE toLower(s.name) CONTAINS toLower("<keyword>")

OPTIONAL MATCH (s)-[r1:HAS_NETWORK_COST|HAS_OUT_OF_NETWORK_COST]->(costNode)
OPTIONAL MATCH (costNode)-[r2:HAS_COPAY|HAS_COINSURANCE]->(detailNode)
OPTIONAL MATCH (detailNode)-[:VALUE]->(valNode)

RETURN 
    s.name AS entity,
    type(r1) AS cost_type,
    type(r2) AS detail_type,
    detailNode.value,
    costNode.name,
    valNode.value
ORDER BY entity, cost_type, detail_type

-------------------------------
SPECIALIZED PATTERNS
-------------------------------

# Important Questions
MATCH (e:Entity)-[r:ANSWER]->(v:Value)
WHERE toLower(e.name) CONTAINS toLower($k)

RETURN 
    e.name AS entity,
    "ANSWER" AS relationship,
    v.value AS answer

# Overall Deductible / General Fallback
MATCH (e:Entity)
WHERE toLower(e.name) CONTAINS toLower(k)

OPTIONAL MATCH (e)-[r]-(v)

RETURN 
    e.name AS entity,
    type(r) AS relationship,
    coalesce(
        e.answer,
        e.value,
        e.network_cost,
        e.out_of_network_cost,
        v.value,
        v.name
    ) AS result
ORDER BY relationship

#Copay and Coinsurance
MATCH (s:Entity)
WHERE toLower(s.name) CONTAINS toLower(k)

OPTIONAL MATCH (s)-[r1:HAS_NETWORK_COST|HAS_OUT_OF_NETWORK_COST]->(costNode)
OPTIONAL MATCH (costNode)-[r2:HAS_COPAY|HAS_COINSURANCE]->(detailNode)
OPTIONAL MATCH (detailNode)-[:VALUE]->(valNode)   

RETURN 
    s.name AS entity,
    type(r1) AS cost_type,
    type(r2) AS detail_type,
    coalesce(
        valNode.value,       
        detailNode.name,
        costNode.name
    ) AS result
ORDER BY entity, cost_type, detail_type

# Covered Services
MATCH (p:Entity)-[:COVERS_SERVICE]->(s:Entity)
WHERE toLower(p.name) CONTAINS toLower(k)
RETURN 
    p.name AS plan,
    s.name AS covered_service
ORDER BY covered_service

# Service + Cost
MATCH (s:Entity)
WHERE any(k IN $keywords WHERE toLower(s.name) CONTAINS toLower(k))

OPTIONAL MATCH (s)-[r1:HAS_NETWORK_COST|HAS_OUT_OF_NETWORK_COST]->(costNode)
OPTIONAL MATCH (costNode)-[r2:HAS_COPAY|HAS_COINSURANCE]->(detailNode)
OPTIONAL MATCH (s)-[r3:HAS_LIMITATION]->(limNode)
OPTIONAL MATCH (s)-[r4:REQUIRES]->(req)

RETURN 
    s.name AS entity,
    coalesce(type(r2), type(r1), type(r3), type(r4)) AS relationship,
    coalesce(
        detailNode.value,
        costNode.raw,
        limNode.text,
        req.name
    ) AS result
ORDER BY entity, relationship

# Network / Out-of-network Cost
MATCH (s:Entity)
WHERE toLower(s.name) CONTAINS toLower(k)

OPTIONAL MATCH (s)-[:RAW]->(rawNode)

OPTIONAL MATCH (s)-[r1:HAS_NETWORK_COST|HAS_OUT_OF_NETWORK_COST]->(costNode)
OPTIONAL MATCH (costNode)-[r2:HAS_COPAY|HAS_COINSURANCE]->(detailNode)
OPTIONAL MATCH (detailNode)-[:VALUE]->(valNode)

RETURN 
    s.name AS entity,
    type(r1) AS cost_type,
    type(r2) AS detail_type,
    coalesce(
        rawNode.value,
        valNode.value,
        detailNode.name,
        costNode.raw
    ) AS result
ORDER BY entity

# Limitations 
MATCH (s:Entity)
WHERE toLower(s.name) CONTAINS toLower($k)

OPTIONAL MATCH (s)-[:HAS_LIMITATION]->(lim)

OPTIONAL MATCH (lim)-[:TEXT]->(v:Value)

RETURN 
    s.name AS entity,
    "HAS_LIMITATION" AS relationship,
    coalesce(v.value, lim.text, lim.name) AS result
ORDER BY entity

# Not Covered / Exclusions 
MATCH (p:Entity)-[:EXCLUDES_SERVICE]->(s:Entity)
RETURN 
    p.name AS healthplan,
    s.name AS covered_service

# Preauthorization / Requirements
MATCH (s:Entity)
WHERE any(k IN $keywords WHERE toLower(s.name) CONTAINS toLower(k))

OPTIONAL MATCH (s)-[:REQUIRES]->(req)

RETURN 
    s.name AS entity,
    "REQUIRES" AS relationship,
    req.name AS result
ORDER BY entity

-------------------------------

#EXAMPLES

Q: Are there services covered before you meet your deductible?
A:
MATCH (e:Entity)-[:ANSWER]->(v:Value)
WHERE toLower(e.name) CONTAINS toLower("services covered before you meet your deductible")
   OR toLower(e.name) CONTAINS toLower("covered before deductible")

RETURN 
    e.name AS entity,
    "ANSWER" AS relationship,
    v.value AS answer

Q: Are there other deductibles for specific services?
A:
MATCH (e:Entity)-[r:ANSWER]->(v:Value)
WHERE toLower(e.name) CONTAINS toLower("other deductibles")
   OR toLower(e.name) CONTAINS toLower("specific services")

RETURN 
    e.name AS entity,
    "ANSWER" AS relationship,
    v.value AS answer

Q: What is the out-of-pocket limit for this plan?
A:
MATCH (e:Entity)-[r:ANSWER]->(v:Value)
WHERE toLower(e.name) CONTAINS toLower("out-of-pocket limit for this plan")

RETURN 
    e.name AS entity,
    "ANSWER" AS relationship,
    v.value AS answer

Q: What are the other covered services?
A:
MATCH (p:Entity)-[:COVERS_SERVICE]->(s:Entity)
RETURN 
    p.name AS healthplan,
    s.name AS covered_service

Q: What is not included in the out-of-pocket limit?
A:
MATCH (e:Entity)-[r:ANSWER]->(v:Value)
WHERE toLower(e.name) CONTAINS toLower("not included in the out-of-pocket limit")

RETURN 
    e.name AS entity,
    "ANSWER" AS relationship,
    v.value AS answer

Q: Do you need a referral to see a specialist?
A:
MATCH (e:Entity)-[r:ANSWER]->(v:Value)
WHERE toLower(e.name) CONTAINS toLower("referral to see a specialist")

RETURN 
    e.name AS entity,
    "ANSWER" AS relationship,
    v.value AS answer

-------------------------
QUESTION:
{question}

First extract important keywords from the question, then generate the BEST Cypher query.
"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "http://localhost",
        "X-Title": "SBC Cypher Generator",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "meta-llama/llama-4-maverick",
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

       