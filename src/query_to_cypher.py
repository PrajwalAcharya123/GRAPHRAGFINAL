# src/query_to_cypher.py
from groq import Groq
import os
from dotenv import load_dotenv
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# def question_to_cypher(question):
#     prompt = f"""
#     You are an expert Neo4j Cypher generator for a health insurance knowledge graph.

#     Convert the user question into a Cypher query.

#     GRAPH SCHEMA:

#     Nodes:
#     - (Entity {{name}})
#     - (Value {{name}})

#     Important Relationship Types:
#     - BELONGS_TO
#     - HAS_NETWORK_COST
#     - HAS_OUT_NETWORK_COST
#     - HAS_LIMITATION
#     - HAS_DEDUCTIBLE
#     - HAS_OUT_OF_POCKET_LIMIT
#     - HAS_SERVICE
#     - HAS_COVERAGE

#     Structure patterns:
#     - (Service)-[:BELONGS_TO]->(MedicalEvent)
#     - (Service)-[:HAS_NETWORK_COST]->(Value)
#     - (Service)-[:HAS_OUT_NETWORK_COST]->(Value)
#     - (Service)-[:HAS_LIMITATION]->(Value)
#     - (Plan)-[:HAS_DEDUCTIBLE]->(Value)

#     RULES:

#     1. Return ONLY Cypher query (no explanation)
#     2. Always use MATCH
#     3. Use WHERE with CONTAINS for fuzzy search
#     4. Return meaningful fields (entity names and values)
#     5. Use aliases like e, v, r
#     6. Prefer patterns like:
#     MATCH (e:Entity)-[r]->(v:Value)

#     7. If question is about cost:
#     search HAS_NETWORK_COST and HAS_OUT_NETWORK_COST

#     8. If question is about deductible or limits:
#     search Plan node

#     ALWAYS return relationship-based results:
#     MATCH (e:Entity)-[r]->(v:Value)
#     RETURN e.name, type(r), v.name

#     EXAMPLES:

#     Q: What is the cost of primary care visit?
#     A:
#     MATCH (e:Entity)-[r]->(v:Value)
#     WHERE e.name CONTAINS "Primary care visit"
#     AND (type(r) = "HAS_NETWORK_COST" OR type(r) = "HAS_OUT_NETWORK_COST")
#     RETURN e.name, type(r), v.name

#     Q: What is the deductible?
#     A:
#     MATCH (e:Entity)-[r]->(v:Value)
#     WHERE e.name CONTAINS "Plan"
#     AND type(r) = "HAS_DEDUCTIBLE"
#     RETURN e.name, v.name

#     Q: What services belong to emergency care?
#     A:
#     MATCH (s:Entity)-[:BELONGS_TO]->(e:Entity)
#     WHERE e.name CONTAINS "Emergency"
#     RETURN s.name

#     Q: What are the limitations of specialist visit?
#     A:
#     MATCH (e:Entity)-[:HAS_LIMITATION]->(v:Value)
#     WHERE e.name CONTAINS "Specialist visit"
#     RETURN e.name, v.name

#     QUESTION:
#     {question}
#     """
def question_to_cypher(question):
    prompt = f"""
You are a Neo4j Cypher generator.

Convert the user question into a Cypher query.

STRICT RULES:

1. Return ONLY Cypher query (no explanation, no text)
2. Choose correct pattern based on relationship:

   - For cost-related data (COPAY, COST, DEDUCTIBLE, etc.):
     MATCH (e:Entity)-[r]->(v:Value)

   - For relationship between entities (BELONGS_TO):
     MATCH (e:Entity)-[r:BELONGS_TO]->(v:Entity)

3. Use case-insensitive matching:
   WHERE toLower(e.name) CONTAINS "<keyword>"

4. VALID relationship types (ONLY use these):
   - COPAY
   - COPAYMENT
   - COST
   - DEDUCTIBLE
   - COINSURANCE
   - LIMIT
   - LIMITATION

5. Map question → relationship:

   - "copay", "copayment" → COPAY or COPAYMENT
   - "cost", "price", "charge" → COST
   - "deductible" → DEDUCTIBLE
   - "coinsurance" → COINSURANCE
   - "limit" → LIMIT or LIMITATION

6. NEVER use:
   HAS_NETWORK_COST
   HAS_OUT_NETWORK_COST
   HAS_DEDUCTIBLE
   or any other invented relationship

7. Extract the main entity from the question and use it in CONTAINS

8. Always return:
   RETURN e.name, type(r), v.name

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
A:
MATCH (e:Entity)-[r]->(v:Value)
WHERE toLower(e.name) CONTAINS "deductible"
AND type(r) = "DEDUCTIBLE"
RETURN e.name, type(r), v.name

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