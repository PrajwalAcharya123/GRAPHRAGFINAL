# # src/jsonld_chunker.py
# import json
# import os

# def chunk_jsonld(input_path, output_path):
#     with open(input_path, "r", encoding="utf-8") as f:
#         data = json.load(f)

#     graph = data.get("@graph", [])

#     chunks = []
#     node_map = {}

#     # 🔹 Separate nodes and relations
#     for item in graph:
#         if "@id" in item:
#             node_map[item["@id"]] = item

#     # 🔹 Build chunks
#     for item in graph:
#         if item.get("@type") == "Relation":
#             continue

#         node_id = item.get("@id")

#         if not node_id:
#             continue

#         # Find relations for this node
#         relations = [
#             r for r in graph
#             if r.get("@type") == "Relation" and r.get("to") == node_id
#         ]

#         chunk = {
#             "chunk_id": f"chunk_{node_id}",
#             "type": item.get("@type"),
#             "content": {k: v for k, v in item.items() if not k.startswith("@")},
#             "relations": relations
#         }

#         chunks.append(chunk)
#     # 💾 Save chunks
#     os.makedirs(os.path.dirname(output_path), exist_ok=True)

#     with open(output_path, "w", encoding="utf-8") as f:
#         json.dump(chunks, f, indent=2)

#     print(f"✅ Chunked JSON saved: {output_path}")

#     return chunks




# src/jsonld_chunker.py

import json
import os


def chunk_jsonld(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    graph = data.get("@graph", [])

    chunks = []
    node_map = {}
    relations = []

    # =========================
    # 🔹 Separate nodes & relations
    # =========================
    for item in graph:
        if "@id" in item:
            node_map[item["@id"]] = item
        elif "from" in item and "to" in item:
            relations.append(item)

    # =========================
    # 🔹 Build Graph-aware chunks
    # =========================
    for node_id, node in node_map.items():

        connected_relations = []
        connected_nodes = {}

        for rel in relations:
            if rel["from"] == node_id or rel["to"] == node_id:
                connected_relations.append(rel)

                # Add neighbor nodes
                from_id = rel["from"]
                to_id = rel["to"]

                if from_id in node_map:
                    connected_nodes[from_id] = node_map[from_id]

                if to_id in node_map:
                    connected_nodes[to_id] = node_map[to_id]

        chunk = {
            "chunk_id": f"chunk_{node_id}",
            "main_node": node,
            "connected_nodes": list(connected_nodes.values()),
            "relations": connected_relations
        }

        chunks.append(chunk)

    # =========================
    # 💾 SAVE
    # =========================
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2)

    print(f"✅ Structured chunks saved: {output_path}")
    return chunks