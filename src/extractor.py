
# src/extractor.py

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
def clean_llm_output(text):
    text = re.sub(r"```json", "", text)
    text = re.sub(r"```", "", text)

    match = re.search(r"\{.*\}", text, re.DOTALL)
    return match.group(0).strip() if match else text.strip()


# =========================
# 🔥 CONVERT CHUNK → TEXT
# =========================
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

def chunk_to_text(chunk):
    if chunk.get("type") == "table_row":
        data = chunk.get("data", {})
        parts = []
        for key, value in data.items():
            if value:
                parts.append(f"{key}: {value}")
        return ". ".join(parts)

    elif chunk.get("type") == "section":
        return f"{chunk.get('title', '')}. {chunk.get('content', '')}"

    elif chunk.get("type") == "list":
        return " ".join(chunk.get("items", []))

    # 🔥 ADD THIS (CRITICAL FIX)
    elif chunk.get("type") in ["paragraph", "text"]:
        return chunk.get("content", "")

    # 🔥 fallback (VERY IMPORTANT)
    return str(chunk)


def extract_graph(text):
    prompt = f"""
            
            You are an expert system for extracting COMPLETE structured knowledge graphs from health insurance SBC documents.

            Your goal is to extract ALL meaningful structured data from the document, including:
            - entities
            - relationships
            - attributes
            - numeric values
            - conditions
            - limits
            - coverage rules

            Output ONLY valid JSON in this format:

            {{
            "entities": [],
            "relationships": [],
            "attributes": []
            }}

            ----------------------
            EXTRACTION GUIDELINES:
            ----------------------

            1. ENTITIES:
            Extract ALL important entities including:
            - Plans (e.g., "Plan Option 1")
            - Services (e.g., "Primary care visit", "Emergency room care")
            - Medical events (e.g., "Pregnancy", "Hospital stay")
            - Cost types (e.g., "Copay", "Coinsurance", "Deductible")
            - Coverage types (e.g., "Preventive care", "Out-of-network provider")
            - Conditions (e.g., "Preauthorization")

            2. RELATIONSHIPS:
            Extract structured relationships:
            - HAS_COPAY
            - HAS_COINSURANCE
            - HAS_DEDUCTIBLE
            - HAS_LIMIT
            - REQUIRES
            - COVERS
            - NOT_COVERED
            - APPLIES_TO
            - REDUCES_BENEFIT

            Example:
            ["Specialist visit", "HAS_COPAY", "$50"]

            3. ATTRIBUTES:
            Extract ALL numeric and descriptive values:
            - dollar amounts ($500, $35)
            - percentages (20%, 40%)
            - counts (60 visits/year)
            - coverage limits
            - plan details

            Example:
            ["Deductible", "individual", "$500"]

            4. TABLE EXTRACTION:
            Convert table rows into structured triples:
            Each row should produce:
            - entity (service)
            - attributes (costs)
            - relationships

            Example:
            {{
            "service": "Primary care visit",
            "network_cost": "$35 copay",
            "out_of_network_cost": "40% coinsurance",
            "conditions": "deductible does not apply"
            }}

            5. RULES & CONDITIONS:
            Extract rules like:
            - "Preauthorization is required"
            - "Failure results in 50% reduction"

            Example:
            ["Specialist visit", "REQUIRES", "Preauthorization"]
            ["No preauthorization", "REDUCES_BENEFIT", "50%"]

            6. COVERAGE:
            Capture:
            - covered services
            - excluded services
            - limitations

            Example:
            ["Cosmetic surgery", "NOT_COVERED", "Plan"]
            ["Home health care", "HAS_LIMIT", "60 visits/year"]

            7. SCENARIOS:
            Extract example cost breakdowns:

            Example:
            {{
            "scenario": "Pregnancy",
            "total_cost": "$12,800",
            "patient_pays": "$3,160"
            }}

            ----------------------
            CRITICAL RULES:
            ----------------------

            - Extract EVERYTHING meaningful (not just costs)
            - Include ALL numeric values
            - Normalize entity names
            - Do NOT miss tables
            - Do NOT summarize
            - Do NOT explain
            - Output ONLY JSON

            ----------------------
            TEXT:
            {text}
            """


    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    raw_output = response.choices[0].message.content

    print("\n🔍 RAW LLM OUTPUT:\n", raw_output)

    cleaned = clean_llm_output(raw_output)

    try:
        parsed = json.loads(cleaned)
    except Exception as e:
        print("❌ JSON parse failed:", e)
        parsed = {"entities": [], "relationships": [], "attributes": []}

    return parsed


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


