# # src/json_to_jsonld.py
# import json
# import os

# def json_to_jsonld(input_path, output_path):
#     # ✅ Ensure .json extension
#     if not output_path.endswith(".json"):
#         output_path += ".json"

#     with open(input_path, "r", encoding="utf-8") as f:
#         data = json.load(f)

#     graph = []

#     # 🔹 Root Plan Node
#     graph.append({
#         "@id": "plan_1",
#         "@type": "HealthPlan",
#         "name": "SBC Plan"
#     })

#     # 🔹 Convert entities → graph nodes
#     for i, entity in enumerate(data.get("entities", [])):
#         node_id = f"node_{i}"

#         node = {
#             "@id": node_id,
#             "@type": entity.get("type", "Entity")
#         }

#         # Normalize keys
#         for k, v in entity.get("attributes", {}).items():
#             clean_key = k.lower().replace(" ", "_")
#             node[clean_key] = v

#         graph.append(node)

#         # 🔥 Relationship to plan
#         graph.append({
#             "@type": "Relation",
#             "from": "plan_1",
#             "to": node_id,
#             "relation": entity.get("type", "related_to")
#         })

#     jsonld = {
#         "@context": "http://schema.org",
#         "@graph": graph
#     }

#     # 💾 Save JSON-LD
#     os.makedirs(os.path.dirname(output_path), exist_ok=True)

#     with open(output_path, "w", encoding="utf-8") as f:
#         json.dump(jsonld, f, indent=2, ensure_ascii=False)

#     print(f"✅ JSON-LD saved at: {output_path}")

#     return jsonld



# src/json_to_jsonld.py

import json
import os


def json_to_jsonld(input_path, output_path):
    if not output_path.endswith(".json"):
        output_path += ".json"

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    graph = []

    # =========================
    # 🔹 ENTITIES → NODES
    # =========================
    for entity in data.get("entities", []):
        node = {
            "@id": entity["id"],
            "@type": entity["type"]
        }

        for k, v in entity.items():
            if k not in ["id", "type"]:
                node[k] = v

        graph.append(node)

    # =========================
    # 🔹 RELATIONSHIPS
    # =========================
    for rel in data.get("relationships", []):
        graph.append({
            "@type": rel["type"],
            "from": rel["from"],
            "to": rel["to"]
        })

    jsonld = {
        "@context": {
            "name": "http://schema.org/name",
            "HealthPlan": "http://schema.org/HealthPlan",
            "MedicalService": "http://schema.org/MedicalService",
            "Cost": "http://example.org/Cost"
        },
        "@graph": graph
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(jsonld, f, indent=2, ensure_ascii=False)

    print(f"✅ JSON-LD saved: {output_path}")

    return jsonld