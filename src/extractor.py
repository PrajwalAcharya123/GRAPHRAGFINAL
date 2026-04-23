# # src/extractor.py
# from groq import Groq
# import os
# import json
# import re
# from dotenv import load_dotenv
# # 🔹 Load environment variables
# load_dotenv()

# # 🔹 Initialize Groq client
# client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# # 🔥 Clean markdown + extract pure JSON
# def clean_llm_output(text):
#     # Remove ```json and ```
#     text = re.sub(r"```json", "", text)
#     text = re.sub(r"```", "", text)

#     # Extract only JSON block
#     match = re.search(r"\{.*\}", text, re.DOTALL)
#     return match.group(0).strip() if match else text.strip()

# def extract_graph(text, chunk_id=None, output_dir="src/output/llm_graph"):

#     prompt = f"""
#             Extract a knowledge graph from health insurance SBC text.

#             Return ONLY JSON:
#             {{
#               "entities": [],
#               "relationships": [],
#               "attributes": []
#             }}

#             Rules:
#             - Service BELONGS_TO MedicalEvent
#             - HAS_NETWORK_COST, HAS_OUT_NETWORK_COST
#             - HAS_LIMITATION, HAS_DEDUCTIBLE, HAS_OUT_OF_POCKET_LIMIT
#             - Keep network vs out-of-network separate
#             - Extract values like $500, 20%, copay
#             - Do NOT explain anything

#             Text:
#             {text}
#             """
#     # 🔹 Call Groq API
#     response = client.chat.completions.create(
#         model="llama-3.3-70b-versatile",
#         messages=[{"role": "user", "content": prompt}],
#         temperature=0
#     )

#     # 🔹 Extract raw content
#     raw_output = response.choices[0].message.content

#     print("\n🔍 LLM RAW OUTPUT:")
#     print(raw_output)

#     # 🔥 Clean output
#     cleaned = clean_llm_output(raw_output)

#     print("\n🧹 CLEANED JSON:")
#     print(cleaned)

#     # 🔹 Safe JSON parsing
#     try:
#         parsed = json.loads(cleaned)
#     except Exception as e:
#         print("❌ JSON parse failed:", e)
#         parsed = {
#             "entities": [],
#             "relationships": [],
#             "attributes": []
#         }

#     # 🔹 Save output
#     if chunk_id:
#         os.makedirs(output_dir, exist_ok=True)
#         file_path = os.path.join(output_dir, f"{chunk_id}.json")

#         with open(file_path, "w", encoding="utf-8") as f:
#             json.dump(parsed, f, indent=2)

#         print(f"💾 Saved: {file_path}")

#     return parsed
















# src/extractor.py

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


# # =========================
# # LLM GRAPH EXTRACTION
# # =========================
# def extract_graph(text):

#     prompt = f"""
# Extract a knowledge graph from health insurance SBC text.

# Return ONLY JSON:
# {{
#   "entities": [],
#   "relationships": [],
#   "attributes": []
# }}

# Rules:
# - Service BELONGS_TO MedicalEvent
# - HAS_NETWORK_COST, HAS_OUT_NETWORK_COST
# - HAS_LIMITATION, HAS_DEDUCTIBLE, HAS_OUT_OF_POCKET_LIMIT
# - Keep network vs out-of-network separate
# - Extract values like $500, 20%, copay
# - Do NOT explain anything

# Text:
# {text}
# """

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

#         if not text.strip():
#             continue

#         print(f"\n🚀 Processing: {chunk_id}")

#         graph = extract_graph(text)

#         # Save per chunk
#         file_path = os.path.join(output_dir, f"{chunk_id}.json")

#         with open(file_path, "w", encoding="utf-8") as f:
#             json.dump(graph, f, indent=2)

#         print(f"💾 Saved: {file_path}")




import os
import json
import re
from groq import Groq
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
# CHUNK → TEXT (IMPORTANT)
# =========================
def chunk_to_text(chunk):

    if chunk["type"] == "table_row":
        return json.dumps(chunk["data"], indent=2)

    elif chunk["type"] == "section":
        return f"{chunk.get('title', '')}\n{chunk.get('content', '')}"

    elif chunk["type"] == "list":
        return "\n".join(chunk.get("items", []))

    return ""


# =========================
# LLM GRAPH EXTRACTION
# =========================
def extract_graph(text):

    prompt = f"""
You are an expert in extracting structured knowledge graphs from health insurance data.

Extract ONLY JSON in this format:

{{
  "entities": ["Entity1", "Entity2"],
  "relationships": [
    ["Entity1", "RELATION", "Entity2"]
  ],
  "attributes": [
    ["Entity", "attribute", "value"]
  ]
}}

Rules:
- Extract medical services, plans, costs, events
- Keep entities short and normalized (e.g., "Deductible", not full sentence)
- Relationships must be meaningful:
    - HAS_COST
    - HAS_DEDUCTIBLE
    - HAS_LIMITATION
    - BELONGS_TO
- Extract values like "$500", "20%", "copay"
- Do NOT explain anything
- Output ONLY valid JSON

Text:
{text}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    raw_output = response.choices[0].message.content

    print("\n🔍 RAW OUTPUT:\n", raw_output)

    cleaned = clean_llm_output(raw_output)

    try:
        parsed = json.loads(cleaned)
    except Exception as e:
        print("❌ JSON parse failed:", e)
        parsed = {"entities": [], "relationships": [], "attributes": []}

    return parsed


# =========================
# PROCESS ALL CHUNKS
# =========================
def process_chunks(chunk_path, output_path, batch_size=10):

    with open(chunk_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    all_graphs = []

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]

        print(f"\n🚀 Processing batch {i//batch_size}")

        # ✅ BEST: send structured batch
        text = json.dumps(batch, indent=2)

        graph = extract_graph(text)

        all_graphs.append(graph)

    # 🔹 Merge all
    final_graph = {
        "entities": [],
        "relationships": [],
        "attributes": []
    }

    for g in all_graphs:
        final_graph["entities"].extend(g.get("entities", []))
        final_graph["relationships"].extend(g.get("relationships", []))
        final_graph["attributes"].extend(g.get("attributes", []))

    # 🔹 Deduplicate
    final_graph["entities"] = list(set(final_graph["entities"]))

    final_graph["relationships"] = list(set(
        tuple(r) for r in final_graph["relationships"]
    ))
    final_graph["relationships"] = [list(r) for r in final_graph["relationships"]]

    final_graph["attributes"] = list(set(
        tuple(a) for a in final_graph["attributes"]
    ))
    final_graph["attributes"] = [list(a) for a in final_graph["attributes"]]

    # 🔹 Save output
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_graph, f, indent=2)

    print(f"\n✅ Graph saved at: {output_path}")

    return final_graph