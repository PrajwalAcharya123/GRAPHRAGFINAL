# # src/chunk_to_graph.py

# from extractor import extract_graph
# from neo4j_handler import Neo4jHandler
# import json
# import os

# def process_chunks(chunk_path, output_dir, batch_size=5):
#     with open(chunk_path, "r", encoding="utf-8") as f:
#         chunks = json.load(f)

#     llm_output_dir = os.path.join(output_dir, "llm_graph")
#     neo4j = Neo4jHandler()

#     # 🔥 Group chunks into batches
#     for i in range(0, len(chunks), batch_size):
#         batch = chunks[i:i + batch_size]

#         batch_id = f"batch_{i//batch_size}"

#         # 🔥 Combine texts
#         combined_text = "\n\n".join([
#             json.dumps(chunk, indent=2) for chunk in batch
#         ])

#         print(f"\n🔍 Processing {batch_id}")

#         graph_data = extract_graph(
#             combined_text,
#             chunk_id=batch_id,
#             output_dir=llm_output_dir
#         )

#         neo4j.insert_graph_data(graph_data)

#     neo4j.close()
#     print("✅ All batches inserted into Neo4j")



# from extractor import extract_graph
# from neo4j_handler import Neo4jHandler
# import json
# import os


# # ✅ Normalize relationships (fix KeyError issue)
# def normalize_graph(graph_data):
#     normalized_rels = []

#     for rel in graph_data.get("relationships", []):
#         if isinstance(rel, list):
#             normalized_rels.append(rel)

#         elif isinstance(rel, dict):
#             normalized_rels.append([
#                 rel.get("entity1"),
#                 rel.get("type"),
#                 rel.get("entity2")
#             ])

#     graph_data["relationships"] = normalized_rels
#     return graph_data


# # ✅ Merge all batch outputs
# def merge_graphs(all_graphs):
#     final_graph = {
#         "entities": [],
#         "relationships": [],
#         "attributes": []
#     }

#     for g in all_graphs:
#         final_graph["entities"].extend(g.get("entities", []))
#         final_graph["relationships"].extend(g.get("relationships", []))
#         final_graph["attributes"].extend(g.get("attributes", []))

#     return final_graph


# def process_chunks(chunk_path, output_dir, batch_size=5):
#     with open(chunk_path, "r", encoding="utf-8") as f:
#         chunks = json.load(f)

#     llm_output_dir = os.path.join(output_dir, "llm_graph")
#     neo4j = Neo4jHandler()

#     all_graphs = []   # ✅ collect everything first

#     for i in range(0, len(chunks), batch_size):
#         batch = chunks[i:i + batch_size]
#         batch_id = f"batch_{i//batch_size}"

#         # ⚡ Reduce token usage (VERY IMPORTANT)
#         combined_text = "\n\n".join([
#             chunk.get("text", "") for chunk in batch   # ✅ instead of json.dumps
#         ])

#         print(f"\n🔍 Processing {batch_id}")

#         graph_data = extract_graph(
#             combined_text,
#             chunk_id=batch_id,
#             output_dir=llm_output_dir
#         )

#         # ✅ Fix structure issue
#         graph_data = normalize_graph(graph_data)

#         all_graphs.append(graph_data)

#     # ✅ Merge everything
#     final_graph = merge_graphs(all_graphs)

#     print("\n🚀 Inserting ALL data into Neo4j (single call)")

#     neo4j.insert_graph_data(final_graph)

#     neo4j.close()
#     print("✅ Done")




from extractor import extract_graph
from neo4j_handler import Neo4jHandler
import json
import os


# 🔥 Normalize relationships + attributes (FIXES KeyError + format issues)
def normalize_graph(graph_data):
    normalized_rels = []
    normalized_attrs = []

    # ✅ Normalize relationships
    for rel in graph_data.get("relationships", []):
        if isinstance(rel, list) and len(rel) == 3:
            normalized_rels.append(rel)

        elif isinstance(rel, dict):
            e1 = rel.get("entity1")
            r = rel.get("type")
            e2 = rel.get("entity2")

            if e1 and r and e2:
                normalized_rels.append([e1, r, e2])

    # ✅ Normalize attributes
    for attr in graph_data.get("attributes", []):
        if isinstance(attr, list) and len(attr) == 3:
            normalized_attrs.append(attr)

        elif isinstance(attr, dict):
            entity = attr.get("entity")
            key = attr.get("attribute")
            value = attr.get("value")

            if entity and key and value:
                normalized_attrs.append([entity, key, value])

    graph_data["relationships"] = normalized_rels
    graph_data["attributes"] = normalized_attrs

    return graph_data


# 🔥 Remove duplicates (VERY IMPORTANT for Neo4j)
def deduplicate_graph(graph):
    graph["entities"] = list(set(graph.get("entities", [])))

    graph["relationships"] = list(set(
        tuple(r) for r in graph.get("relationships", [])
    ))

    graph["attributes"] = list(set(
        tuple(a) for a in graph.get("attributes", [])
    ))

    # Convert back to list
    graph["relationships"] = [list(r) for r in graph["relationships"]]
    graph["attributes"] = [list(a) for a in graph["attributes"]]

    return graph


# 🔥 Merge all batch outputs
def merge_graphs(all_graphs):
    final_graph = {
        "entities": [],
        "relationships": [],
        "attributes": []
    }

    for g in all_graphs:
        final_graph["entities"].extend(g.get("entities", []))
        final_graph["relationships"].extend(g.get("relationships", []))
        final_graph["attributes"].extend(g.get("attributes", []))

    return final_graph


def process_chunks(chunk_path, output_dir, batch_size=5):
    with open(chunk_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    llm_output_dir = os.path.join(output_dir, "llm_graph")
    neo4j = Neo4jHandler()

    all_graphs = []

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        batch_id = f"batch_{i//batch_size}"

        # ⚡ Efficient text combination (token optimized)
        combined_text = "\n\n".join([
            chunk.get("text", "") for chunk in batch
            if chunk.get("text")
        ])

        if not combined_text.strip():
            continue

        print(f"\n🔍 Processing {batch_id}")

        graph_data = extract_graph(
            combined_text,
            chunk_id=batch_id,
            output_dir=llm_output_dir
        )

        # ✅ Normalize structure
        graph_data = normalize_graph(graph_data)

        all_graphs.append(graph_data)

    # ✅ Merge all batches
    final_graph = merge_graphs(all_graphs)

    # ✅ Deduplicate (CRITICAL)
    final_graph = deduplicate_graph(final_graph)

    print("\n🚀 Inserting ALL data into Neo4j (single call)")

    neo4j.insert_graph_data(final_graph)
    neo4j.close()

    print("✅ Done")



# import json
# import os


# def process_chunks(input_path, output_path):
#     with open(input_path, "r", encoding="utf-8") as f:
#         data = json.load(f)

#     graph = data#.get("@graph", [])

#     chunks = []
#     node_map = {}
#     relations = []

#     # =========================
#     # 🔹 Separate nodes & relations
#     # =========================
#     for item in graph:
#         if "@id" in item:
#             node_map[item["@id"]] = item
#         elif "from" in item and "to" in item:
#             relations.append(item)

#     # =========================
#     # 🔹 Build Clean Chunks
#     # =========================
#     for node_id, node in node_map.items():

#         main_name = node.get("name", node_id)

#         connected_nodes = set()
#         relation_strings = []

#         for rel in relations:
#             if rel["from"] == node_id or rel["to"] == node_id:

#                 from_id = rel["from"]
#                 to_id = rel["to"]
#                 rel_type = rel.get("type", "RELATED_TO")

#                 from_name = node_map.get(from_id, {}).get("name", from_id)
#                 to_name = node_map.get(to_id, {}).get("name", to_id)

#                 # Add connected nodes
#                 if from_id != node_id:
#                     connected_nodes.add(from_name)
#                 if to_id != node_id:
#                     connected_nodes.add(to_name)

#                 # Create readable relation string
#                 relation_strings.append(
#                     f"{from_name} {rel_type} {to_name}"
#                 )

#         chunk = {
#             "main_node": main_name,
#             "connected_nodes": list(connected_nodes),
#             "relations": relation_strings
#         }

#         chunks.append(chunk)

#     # =========================
#     # 💾 SAVE
#     # =========================
#     os.makedirs(os.path.dirname(output_path), exist_ok=True)

#     with open(output_path, "w", encoding="utf-8") as f:
#         json.dump(chunks, f, indent=2)

#     print(f"✅ Clean chunks saved: {output_path}")
#     return chunks