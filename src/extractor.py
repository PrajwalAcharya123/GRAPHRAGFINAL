# src/extractor.py
from groq import Groq
import os
import json
import re
from dotenv import load_dotenv
# 🔹 Load environment variables
load_dotenv()

# 🔹 Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# 🔥 Clean markdown + extract pure JSON
def clean_llm_output(text):
    # Remove ```json and ```
    text = re.sub(r"```json", "", text)
    text = re.sub(r"```", "", text)

    # Extract only JSON block
    match = re.search(r"\{.*\}", text, re.DOTALL)
    return match.group(0).strip() if match else text.strip()


# def extract_graph(text, chunk_id=None, output_dir="src/output/llm_graph"):

    # prompt = f"""
    # You are extracting a KNOWLEDGE GRAPH from a health insurance SBC document.

    # Return ONLY valid JSON:

    # {{
    #   "entities": [],
    #   "relationships": [
    #     ["entity1", "relation", "entity2"]
    #   ],
    #   "attributes": [
    #     ["entity", "attribute", "value"]
    #   ]
    # }}

    # IMPORTANT RULES:

    # 1. Understand TABLE STRUCTURE:
    #   - "Common Medical Event" → category
    #   - "Service" → entity
    #   - "Network Provider" → cost type
    #   - "Out-of-Network Provider" → cost type
    #   - "Limitations" → constraints

    # 2. Extract RELATIONS like:

    #   - Service BELONGS_TO MedicalEvent
    #   - Service HAS_NETWORK_COST Value
    #   - Service HAS_OUT_NETWORK_COST Value
    #   - Service HAS_LIMITATION Value
    #   - Plan HAS_DEDUCTIBLE Value
    #   - Plan HAS_OUT_OF_POCKET_LIMIT Value

    # 3. Extract NUMERIC values:
    #   - $500, $35 copay, 20%, 40%

    # 4. Preserve CONTEXT:
    #   Example:
    #   "Primary care visit" belongs to "health care provider visit"

    # 5. Normalize relation names:
    #   - use uppercase with underscore (HAS_COST, BELONGS_TO)

    # 6. VERY IMPORTANT:
    #   - DO NOT merge columns incorrectly
    #   - DO NOT lose network vs out-of-network distinction

    # 7. Example:

    # Input:
    # Primary care visit → $35 copay → 40% coinsurance

    # Output:
    # {{
    #   "entities": ["Primary care visit"],
    #   "relationships": [
    #     ["Primary care visit", "HAS_NETWORK_COST", "$35 copay"],
    #     ["Primary care visit", "HAS_OUT_NETWORK_COST", "40% coinsurance"]
    #   ],
    #   "attributes": []
    # }}

    # Text:
    # {text}
    # """
def extract_graph(text, chunk_id=None, output_dir="src/output/llm_graph"):

    prompt = f"""
            Extract a knowledge graph from health insurance SBC text.

            Return ONLY JSON:
            {{
              "entities": [],
              "relationships": [],
              "attributes": []
            }}

            Rules:
            - Service BELONGS_TO MedicalEvent
            - HAS_NETWORK_COST, HAS_OUT_NETWORK_COST
            - HAS_LIMITATION, HAS_DEDUCTIBLE, HAS_OUT_OF_POCKET_LIMIT
            - Keep network vs out-of-network separate
            - Extract values like $500, 20%, copay
            - Do NOT explain anything

            Text:
            {text}
            """
    # 🔹 Call Groq API
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    # 🔹 Extract raw content
    raw_output = response.choices[0].message.content

    print("\n🔍 LLM RAW OUTPUT:")
    print(raw_output)

    # 🔥 Clean output
    cleaned = clean_llm_output(raw_output)

    print("\n🧹 CLEANED JSON:")
    print(cleaned)

    # 🔹 Safe JSON parsing
    try:
        parsed = json.loads(cleaned)
    except Exception as e:
        print("❌ JSON parse failed:", e)
        parsed = {
            "entities": [],
            "relationships": [],
            "attributes": []
        }

    # 🔹 Save output
    if chunk_id:
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, f"{chunk_id}.json")

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(parsed, f, indent=2)

        print(f"💾 Saved: {file_path}")

    return parsed