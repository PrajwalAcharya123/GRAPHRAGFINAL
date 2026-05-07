
# # src/extractor.py

# from groq import Groq
# import os
# import json
# import re
# from dotenv import load_dotenv

# load_dotenv()

# client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# # =========================
# # CLEAN LLM OUTPUT
# # =========================
# def clean_llm_output(text):
#     text = re.sub(r"```json", "", text)
#     text = re.sub(r"```", "", text)

#     match = re.search(r"\{.*\}", text, re.DOTALL)
#     return match.group(0).strip() if match else text.strip()


# # =========================
# # 🔥 CONVERT CHUNK → TEXT
# # =========================
# def chunk_to_text(chunk):
#     if chunk["type"] == "table_row":
#         data = chunk["data"]

#         # Convert structured row into readable sentence
#         parts = []
#         for key, value in data.items():
#             if value:
#                 parts.append(f"{key}: {value}")

#         return ". ".join(parts)

#     elif chunk["type"] == "section":
#         return f"{chunk.get('title', '')}. {chunk.get('content', '')}"

#     elif chunk["type"] == "list":
#         return " ".join(chunk.get("items", []))

#     return ""


# def extract_graph(text):
#     prompt = f"""
            
#             You are an expert system for extracting COMPLETE structured knowledge graphs from health insurance SBC documents.

#             Your goal is to extract ALL meaningful structured data from the document, including:
#             - entities
#             - relationships
#             - attributes
#             - numeric values
#             - conditions
#             - limits
#             - coverage rules

#             Output ONLY valid JSON in this format:

#             {{
#             "entities": [],
#             "relationships": [],
#             "attributes": [],
#             "tables": [],
#             "rules": []
#             }}

#             ----------------------
#             EXTRACTION GUIDELINES:
#             ----------------------

#             1. ENTITIES:
#             Extract ALL important entities including:
#             - Plans (e.g., "Plan Option 1")
#             - Services (e.g., "Primary care visit", "Emergency room care")
#             - Medical events (e.g., "Pregnancy", "Hospital stay")
#             - Cost types (e.g., "Copay", "Coinsurance", "Deductible")
#             - Coverage types (e.g., "Preventive care", "Out-of-network provider")
#             - Conditions (e.g., "Preauthorization")

#             2. RELATIONSHIPS:
#             Extract structured relationships:
#             - HAS_COPAY
#             - HAS_COINSURANCE
#             - HAS_DEDUCTIBLE
#             - HAS_LIMIT
#             - REQUIRES
#             - COVERS
#             - NOT_COVERED
#             - APPLIES_TO
#             - REDUCES_BENEFIT

#             Example:
#             ["Specialist visit", "HAS_COPAY", "$50"]

#             3. ATTRIBUTES:
#             Extract ALL numeric and descriptive values:
#             - dollar amounts ($500, $35)
#             - percentages (20%, 40%)
#             - counts (60 visits/year)
#             - coverage limits
#             - plan details

#             Example:
#             ["Deductible", "individual", "$500"]

#             4. TABLE EXTRACTION:
#             Convert table rows into structured triples:
#             Each row should produce:
#             - entity (service)
#             - attributes (costs)
#             - relationships

#             Example:
#             {{
#             "service": "Primary care visit",
#             "network_cost": "$35 copay",
#             "out_of_network_cost": "40% coinsurance",
#             "conditions": "deductible does not apply"
#             }}

#             5. RULES & CONDITIONS:
#             Extract rules like:
#             - "Preauthorization is required"
#             - "Failure results in 50% reduction"

#             Example:
#             ["Specialist visit", "REQUIRES", "Preauthorization"]
#             ["No preauthorization", "REDUCES_BENEFIT", "50%"]

#             6. COVERAGE:
#             Capture:
#             - covered services
#             - excluded services
#             - limitations

#             Example:
#             ["Cosmetic surgery", "NOT_COVERED", "Plan"]
#             ["Home health care", "HAS_LIMIT", "60 visits/year"]

#             7. SCENARIOS:
#             Extract example cost breakdowns:

#             Example:
#             {{
#             "scenario": "Pregnancy",
#             "total_cost": "$12,800",
#             "patient_pays": "$3,160"
#             }}

#             ----------------------
#             CRITICAL RULES:
#             ----------------------

#             - Extract EVERYTHING meaningful (not just costs)
#             - Include ALL numeric values
#             - Normalize entity names
#             - Do NOT miss tables
#             - Do NOT summarize
#             - Do NOT explain
#             - Output ONLY JSON

#             ----------------------
#             TEXT:
#             {text}
#             """


#     response = client.chat.completions.create(
#         model="llama-3.3-70b-versatile",
#         messages=[{"role": "user", "content": prompt}],
#         temperature=0
#     )

#     raw_output = response.choices[0].message.content

#     print("\n🔍 RAW LLM OUTPUT:\n", raw_output)

#     cleaned = clean_llm_output(raw_output)

#     try:
#         parsed = json.loads(cleaned)
#     except Exception as e:
#         print("❌ JSON parse failed:", e)
#         parsed = {"entities": [], "relationships": [], "attributes": []}

#     return parsed


# # =========================
# # 🔥 MAIN DRIVER (IMPORTANT)
# # =========================
# def process_chunks(input_file, output_dir="output/llm_graph"):
#     with open(input_file, "r", encoding="utf-8") as f:
#         chunks = json.load(f)

#     os.makedirs(output_dir, exist_ok=True)

#     for chunk in chunks:
#         chunk_id = chunk.get("chunk_id", "unknown")

#         text = chunk_to_text(chunk)
#         print(f"\n📄 Chunk {chunk_id} text:\n{text[:500]}...")  # Print first 500 chars
#         if not text.strip():
#             continue

#         print(f"\n🚀 Processing: {chunk_id}")

#         graph = extract_graph(text)
#         print(f"\n✅ Extracted graph for chunk {chunk_id}:\n{json.dumps(graph, indent=2)}") 
#         # Save per chunk
#         file_path = os.path.join(output_dir, f"{chunk_id}.json")

#         with open(file_path, "w", encoding="utf-8") as f:
#             json.dump(graph, f, indent=2)

#         print(f"💾 Saved: {file_path}")

from groq import Groq
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# =========================
# CLEAN LLM OUTPUT
# =========================
def clean_llm_output(text: str) -> str:
    text = re.sub(r"```json", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```", "", text)
    match = re.search(r"\{.*\}", text, re.DOTALL)
    return match.group(0).strip() if match else text.strip()


# =========================
# CHUNK TO TEXT
# =========================
def chunk_to_text(chunk: dict) -> str:
    chunk_type = chunk.get("type", "")
    
    if chunk_type == "important_question":
        return f"""Question: {chunk.get('question', '')}
Answer: {chunk.get('answer', '')}"""

    elif chunk_type == "benefit_service":
        return f"""Service: {chunk.get('service', '')}
Medical Event: {chunk.get('medical_event', '')}
Network Cost: {chunk.get('network_cost', '')}
Out-of-Network: {chunk.get('out_of_network_cost', '')}
Limitations: {chunk.get('limitations', '')}"""

    elif chunk_type == "plan_metadata":
        return f"Plan: {chunk.get('coverage_for', '')}"

    return str(chunk)


# =========================
# EXTRACT GRAPH - DIRECT RELATIONSHIPS
# =========================
def extract_graph(text: str, chunk_type: str = "", chunk_id: str = ""):
    if chunk_type == "important_question":
        prompt = f"""
You are building a clean knowledge graph for a health insurance plan.

{text}

**Strict Rules:**
- Do NOT store full questions or long answers.
- Create short, meaningful entity names (3-6 words).
- Use **direct, semantic relationships** (no HAS_IMPORTANT_QUESTION).
- Examples of good relationships: HAS_DEDUCTIBLE, HAS_OUT_OF_POCKET_LIMIT, REQUIRES_REFERRAL, COVERS_BEFORE_DEDUCTIBLE, etc.

Output ONLY this JSON format:
{{
  "entities": ["Plan Option 1", "Overall Deductible", "Out-of-Pocket Limit"],
  "relationships": [
    ["Plan Option 1", "HAS_DEDUCTIBLE", "Overall Deductible"],
    ["Plan Option 1", "HAS_OUT_OF_POCKET_LIMIT", "Out-of-Pocket Limit"]
  ],
  "attributes": [
    ["Overall Deductible", "value", "$500 Individual / $1,000 Family"],
    ["Out-of-Pocket Limit", "value", "$2,500 Individual / $5,000 Family"]
  ]
}}
"""
    else:
        prompt = f"""
You are an expert at building clean knowledge graphs.

Chunk Type: {chunk_type}

{text}

Create concise entities and clear UPPER_CASE relationships.
Use direct relationships like HAS_COPAY, HAS_COINSURANCE, HAS_LIMITATION, NOT_COVERED, REQUIRES, etc.

Output ONLY JSON with "entities", "relationships", "attributes".
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=900
        )

        raw_output = response.choices[0].message.content
        cleaned = clean_llm_output(raw_output)
        parsed = json.loads(cleaned)

        parsed.setdefault("entities", [])
        parsed.setdefault("relationships", [])
        parsed.setdefault("attributes", [])

        return parsed

    except Exception as e:
        print(f"❌ Failed for {chunk_id}: {e}")
        return {"entities": [], "relationships": [], "attributes": []}


# =========================
# MAIN PROCESSOR
# =========================
def process_chunks(input_file: str, output_dir: str = "output/llm_graph"):
    with open(input_file, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    os.makedirs(output_dir, exist_ok=True)

    print(f"🚀 Starting clean graph extraction ({len(chunks)} chunks)...\n")

    for chunk in chunks:
        chunk_id = chunk.get("chunk_id", "unknown")
        chunk_type = chunk.get("type", "unknown")

        print(f"📄 Processing {chunk_id} [{chunk_type}]")

        text = chunk_to_text(chunk)
        graph = extract_graph(text, chunk_type, chunk_id)

        file_path = os.path.join(output_dir, f"{chunk_id}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(graph, f, indent=2, ensure_ascii=False)

        print(f"   ✅ Saved {file_path}")

    print("\n🎉 Extraction Completed!")
    return output_dir


