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

def clean_cypher(cypher: str) -> str:
    cypher = cypher.strip()

    # remove markdown fences
    cypher = re.sub(r"```(?:cypher)?", "", cypher)
    cypher = cypher.replace("```", "")

    # remove anything before MATCH/CALL (very important for your bug)
    match = re.search(r"(MATCH|CALL|WITH|UNWIND).*", cypher, re.DOTALL)
    if match:
        cypher = match.group(0)

    return cypher.strip()

def question_to_cypher(question):
    """
    Deterministic Cypher generator aligned with ACTUAL Neo4j structure
    """

    prompt = f"""
You are a STRICT Neo4j Cypher generator.

You MUST follow templates EXACTLY.
DO NOT invent variables.
DO NOT modify query structure.

----------------------------------
REAL GRAPH STRUCTURE (IMPORTANT)
----------------------------------

(:Entity {{name: "Service"}})

(:Entity)-[:INCLUDES_SERVICE]->(:Entity)

Service → HAS_NETWORK_COST → NetworkNode
Service → HAS_OUT_OF_NETWORK_COST → OONNode

NetworkNode → HAS_COPAY → CopayNode
NetworkNode → HAS_COINSURANCE → CoinsNode

NetworkNode → VALUE → ValueNode
CopayNode → VALUE → ValueNode
CoinsNode → VALUE → ValueNode

Service → HAS_LIMITATION → LimitationNode
LimitationNode → TEXT → ValueNode

Service → REQUIRES → Preauthorization

----------------------------------
CRITICAL RULES (DO NOT BREAK)
----------------------------------

1. Return ONLY valid Cypher.

2. ALWAYS use:
   toLower(s.name) CONTAINS toLower("<keyword>")

3. NEVER invent variable names: net_detail_val, oon_detail_val, anything new

4. ONLY use these variables:
   s, net, oon, detail, val

5. VALUE can come from TWO places:
   - (net)-[:VALUE]->(val)
   - (detail)-[:VALUE]->(val)

6. ALWAYS return EXACTLY:
   entity, relationship, result

7. NO explanations. ONLY Cypher.
8. USE the specialized patterns for related questions
9. If the question mentions Peg, Joe or Mia, THEN ALWAYS USE the specialized COVERAGE EXAMPLE Cypher pattern.

---------------------------------
SMART QUERY PATTERNS
---------------------------------
MATCH (s:Entity)-[:QUESTION]->(q:Value)
WHERE toLower(q.value) CONTAINS toLower("<keyword>")

OPTIONAL MATCH (s)-[:INCLUDES_SERVICE]->(svc)
WITH s, q, COALESCE(svc, s) AS target

OPTIONAL MATCH (target)-[:VALUE]->(v:Value)

OPTIONAL MATCH (target)-[:HAS_NETWORK_COST]->(net)
OPTIONAL MATCH (net)-[:VALUE]->(net_val)
OPTIONAL MATCH (net)-[:HAS_COPAY|HAS_COINSURANCE]->(net_detail)

OPTIONAL MATCH (target)-[:HAS_OUT_OF_NETWORK_COST]->(oon)
OPTIONAL MATCH (oon)-[:VALUE]->(oon_val)
OPTIONAL MATCH (oon)-[:HAS_COPAY|HAS_COINSURANCE]->(oon_detail)

RETURN 
    s.name AS matched_entity,
    target.name AS service,
    "QUESTION_MATCH" AS relationship,

    v.value AS result,

    net_val.name AS network_cost,
    net_detail.name AS network_details,

    oon_val.name AS out_of_network_cost,
    oon_detail.name AS out_of_network_details

----------------------------------
SPECIALIZED PATTERNS
----------------------------------

### 1. COPAY/COINSURANCE QUESTIONS
MATCH (s:Entity)
WHERE toLower(s.name) CONTAINS toLower("<keyword>")

OPTIONAL MATCH (s)-[:INCLUDES_SERVICE]->(svc)

WITH s, COALESCE(svc, s) AS target

OPTIONAL MATCH (target)-[:HAS_NETWORK_COST]->(net)
OPTIONAL MATCH (net)-[:VALUE]->(net_val)
OPTIONAL MATCH (net)-[:HAS_COPAY|HAS_COINSURANCE]->(net_detail)

OPTIONAL MATCH (target)-[:HAS_OUT_OF_NETWORK_COST]->(oon)
OPTIONAL MATCH (oon)-[:VALUE]->(oon_val)
OPTIONAL MATCH (oon)-[:HAS_COPAY|HAS_COINSURANCE]->(oon_detail)

RETURN 
    s.name AS matched_entity,
    target.name AS service,
    
    net_val.name AS network_cost,
    net_detail.name AS network_details,

    oon_val.name AS out_of_network_cost,
    oon_detail.name AS out_of_network_details

----------------------------------

### 2. DEDUCTIBLE
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
------------------------------------------
### 3. OUT OF POCKET LIMIT
MATCH (s:Entity)
WHERE s.name = toLower(k)

OPTIONAL MATCH (s)-[:VALUE]->(v:Value)

RETURN 
    s.name AS entity,
    "VALUE" AS relationship,
    v.value AS result
------------------------------------------------
### 4. Out-of-pocket exclusion
MATCH (e:Entity)
WHERE toLower(e.name) = "out-of-pocket exclusions"

OPTIONAL MATCH (e)-[:VALUE]->(v:Value)

RETURN 
    e.name AS entity,
    v.value AS out_of_pocket_exclusion
-------------------------------------------------
### 5. LIMITATIONS

MATCH (s:Entity)
WHERE toLower(s.name) CONTAINS toLower("<keyword>")

OPTIONAL MATCH (s)-[:HAS_LIMITATION]->(lim)
OPTIONAL MATCH (lim)-[:TEXT]->(val)

RETURN 
    s.name AS entity,
    "HAS_LIMITATION" AS relationship,
    val.name AS result
ORDER BY entity

----------------------------------

### 6. PREAUTHORIZATION

MATCH (s:Entity)
WHERE toLower(s.name) CONTAINS toLower("<keyword>")

OPTIONAL MATCH (s)-[:REQUIRES]->(req)

RETURN 
    s.name AS entity,
    "REQUIRES" AS relationship,
    req.name AS result
ORDER BY entity

----------------------------------

### 7. NOT COVERED / EXCLUSIONS

MATCH (h:Entity)-[:EXCLUDES_SERVICE]->(s:Entity)

RETURN 
    h.name AS entity,
    "EXCLUDES_SERVICE" AS relationship,
    s.name AS result
ORDER BY s.name

-----------------------------------

### 8. OTHER COVERED SERVICES
MATCH (p:Entity)-[:COVERS_SERVICE]->(s:Entity)
RETURN 
    p.name AS healthplan,
    s.name AS covered_service

--------------------------------------

### 9. RIGHTS
MATCH (p:Entity)
      -[r]->
      (g:Entity)
WHERE toLower(g.name) CONTAINS toLower("<keyword>")

OPTIONAL MATCH (g)-[:SUMMARY]->(s:Value)

RETURN
    p.name AS plan,
    type(r) AS relationship,
    g.name AS section,
    s.value AS summary
ORDER BY s.value IS NULL
--------------------------------------------

### 12. MINIMUM ESSENTIAL COVERAGE / MINIMUM VALUE STANDARDS
MATCH (p:Entity)
      -[r]->
      (g:Entity)
WHERE toLower(g.name) CONTAINS toLower("<keyword>")

OPTIONAL MATCH (g)-[:SUMMARY]->(s:Value)

RETURN
    p.name AS plan,
    type(r) AS relationship,
    g.name AS section,
    s.value AS summary
ORDER BY s.value IS NULL
------------------------------------------------

### 11. IMPORTANT QUESTIONS
MATCH (s:Entity)-[:QUESTION]->(q:Value)
WHERE toLower(q.value) CONTAINS toLower("<keyword>")

OPTIONAL MATCH (s)-[:VALUE]->(v:Value)

OPTIONAL MATCH (s)-[:HAS_NETWORK_COST]->(net)
OPTIONAL MATCH (net)-[:VALUE]->(net_val)
OPTIONAL MATCH (net)-[:HAS_COPAY|HAS_COINSURANCE]->(net_detail)

OPTIONAL MATCH (s)-[:HAS_OUT_OF_NETWORK_COST]->(oon)
OPTIONAL MATCH (oon)-[:VALUE]->(oon_val)
OPTIONAL MATCH (oon)-[:HAS_COPAY|HAS_COINSURANCE]->(oon_detail)

RETURN 
    s.name AS entity,
    "QUESTION_MATCH" AS relationship,
    v.value AS result,
    net_val.name AS network_cost,
    net_detail.name AS network_details,
    oon_val.name AS out_of_network_cost,
    oon_detail.name AS out_of_network_details

--------------------------------------------------

### 12. COVERAGE EXAMPLES for Questions mentioning Peg, Joe or Mia.

MATCH (root:Entity)
      -[:HAS_SCENARIO]->(scenario:Entity)
WHERE root.name = "Coverage Example Scenarios"


WHERE
    toLower(scenario.name) CONTAINS toLower($scenario)
    OR toLower(scenario.display_name) CONTAINS toLower($scenario)

OPTIONAL MATCH (scenario)-[r]->(node:Entity)

WHERE
    $relationship IS NULL
    OR type(r) = $relationship

RETURN
    scenario.name AS scenario,
    type(r) AS relationship,
    node.name AS node,
    node.description AS description,
    node.amount AS amount

### 13. GENERAL FALLBACK

MATCH (s:Entity)
WHERE toLower(s.name) CONTAINS toLower("<keyword>")

OPTIONAL MATCH (s)-[r]->(n)

RETURN 
    s.name AS entity,
    type(r) AS relationship,
    n.name AS result
ORDER BY entity

----------------------------------


### EXAMPLES

Q: What is the overall deductible?
A:
MATCH (e:Entity)
WHERE e.name = "Overall Deductible"

OPTIONAL MATCH (e)-[r:VALUE]->(v)

RETURN 
    e.name AS entity,
    type(r) AS relationship,
    v.result AS value,


Q: What is not included in the out-of-pocket limit?
A:
MATCH (s:Entity)
WHERE s.name = "Out-of-Pocket Exclusions"

OPTIONAL MATCH (s)-[:VALUE]->(v:Value)

RETURN 
    s.name AS entity,
    "VALUE" AS relationship,
    v.value AS result


Q: Will you pay less if you use a network provider?
A:
MATCH (s:Entity)-[:QUESTION]->(q:Value)
WHERE toLower(q.value) CONTAINS toLower("<keyword>")

OPTIONAL MATCH (s)-[:VALUE]->(v:Value)


RETURN 
    s.name AS entity,
    "QUESTION_MATCH" AS relationship,
    v.value AS result

Q: Does this plan provide minimum essential coverage?
A:
MATCH (p:Entity)
      -[r]->
      (g:Entity)
WHERE toLower(g.name) CONTAINS toLower("<keyword>")

OPTIONAL MATCH (g)-[:SUMMARY]->(s:Value)

RETURN
    p.name AS plan,
    type(r) AS relationship,
    g.name AS section,
    s.value AS summary
ORDER BY s.value IS NULL

Q: What are the other covered services?
A:
MATCH (p:Entity)-[:COVERS_SERVICE]->(s:Entity)
RETURN 
    p.name AS healthplan,
    s.name AS covered_service
------------------------------------

QUESTION:
{question}

OUTPUT:
ONLY Cypher query.
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
        "top_p": 0.1,
        "max_tokens": 500
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

        # Clean markdown
        cypher = re.sub(r"```(?:cypher)?\s*", "", cypher)
        cypher = re.sub(r"```\s*$", "", cypher)

        # cypher = clean_cypher(cypher)
        # return cypher
        return cypher.strip()

    except Exception as e:
        print(f"Cypher generation failed: {e}")