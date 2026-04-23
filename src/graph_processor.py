# from extractor import extract_graph
# from neo4j_handler import Neo4jHandler
# import json
# import os


# # 🔥 Normalize relationships + attributes (FIXES KeyError + format issues)
# def normalize_graph(graph_data):
#     normalized_rels = []
#     normalized_attrs = []

#     # ✅ Normalize relationships
#     for rel in graph_data.get("relationships", []):
#         if isinstance(rel, list) and len(rel) == 3:
#             normalized_rels.append(rel)

#         elif isinstance(rel, dict):
#             e1 = rel.get("entity1")
#             r = rel.get("type")
#             e2 = rel.get("entity2")

#             if e1 and r and e2:
#                 normalized_rels.append([e1, r, e2])

#     # ✅ Normalize attributes
#     for attr in graph_data.get("attributes", []):
#         if isinstance(attr, list) and len(attr) == 3:
#             normalized_attrs.append(attr)

#         elif isinstance(attr, dict):
#             entity = attr.get("entity")
#             key = attr.get("attribute")
#             value = attr.get("value")

#             if entity and key and value:
#                 normalized_attrs.append([entity, key, value])

#     graph_data["relationships"] = normalized_rels
#     graph_data["attributes"] = normalized_attrs

#     return graph_data


# # 🔥 Remove duplicates (VERY IMPORTANT for Neo4j)
# def deduplicate_graph(graph):
#     graph["entities"] = list(set(graph.get("entities", [])))

#     graph["relationships"] = list(set(
#         tuple(r) for r in graph.get("relationships", [])
#     ))

#     graph["attributes"] = list(set(
#         tuple(a) for a in graph.get("attributes", [])
#     ))

#     # Convert back to list
#     graph["relationships"] = [list(r) for r in graph["relationships"]]
#     graph["attributes"] = [list(a) for a in graph["attributes"]]

#     return graph


# # 🔥 Merge all batch outputs
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

#     all_graphs = []

#     for i in range(0, len(chunks), batch_size):
#         batch = chunks[i:i + batch_size]
#         batch_id = f"batch_{i//batch_size}"

#         # ⚡ Efficient text combination (token optimized)
#         combined_text = "\n\n".join([
#             chunk.get("text", "") for chunk in batch
#             if chunk.get("text")
#         ])

#         if not combined_text.strip():
#             continue

#         print(f"\n🔍 Processing {batch_id}")

#         graph_data = extract_graph(
#             combined_text,
#             chunk_id=batch_id,
#             output_dir=llm_output_dir
#         )

#         # ✅ Normalize structure
#         graph_data = normalize_graph(graph_data)

#         all_graphs.append(graph_data)

#     # ✅ Merge all batches
#     final_graph = merge_graphs(all_graphs)

#     # ✅ Deduplicate (CRITICAL)
#     final_graph = deduplicate_graph(final_graph)

#     print("\n🚀 Inserting ALL data into Neo4j (single call)")

#     neo4j.insert_graph_data(final_graph)
#     neo4j.close()

#     print("✅ Done")





# def process_chunks(chunk_path, output_dir):
#     import json
#     from neo4j_handler import Neo4jHandler

#     with open(chunk_path, "r", encoding="utf-8") as f:
#         chunks = json.load(f)

#     neo4j = Neo4jHandler()

#     print("\n🚀 Inserting structured chunks into Neo4j...")

#     for chunk in chunks:

#         service = chunk.get("service")
#         network = chunk.get("network_cost")
#         out_network = chunk.get("out_network_cost")
#         event = chunk.get("event")

#         if not service:
#             continue

#         # ✅ Insert service node
#         neo4j.insert_entity(service)

#         # ✅ Link service to event (context)
#         if event:
#             neo4j.insert_relationship(service, "BELONGS_TO", event)

#         # ✅ Insert costs
#         if network:
#             neo4j.insert_relationship(service, "HAS_NETWORK_COST", network)

#         if out_network:
    #         neo4j.insert_relationship(service, "HAS_OUT_NETWORK_COST", out_network)

    # neo4j.close()
    # print("✅ Graph built successfully")





import json
import os
from extractor import extract_graph
from neo4j_handler import Neo4jHandler


# 🔹 Normalize LLM output
def normalize_graph(graph):
    rels, attrs = [], []

    for r in graph.get("relationships", []):
        if isinstance(r, list) and len(r) == 3:
            rels.append(r)
        elif isinstance(r, dict):
            if r.get("entity1") and r.get("type") and r.get("entity2"):
                rels.append([r["entity1"], r["type"], r["entity2"]])

    for a in graph.get("attributes", []):
        if isinstance(a, list) and len(a) == 3:
            attrs.append(a)
        elif isinstance(a, dict):
            if a.get("entity") and a.get("attribute") and a.get("value"):
                attrs.append([a["entity"], a["attribute"], a["value"]])

    graph["relationships"] = rels
    graph["attributes"] = attrs
    return graph


# 🔹 Normalize + Deduplicate
def deduplicate_graph(graph):
    def norm(x): return x.strip().lower()

    entities = set(norm(e) for e in graph.get("entities", []))

    relationships = set(
        (norm(a), norm(b), norm(c))
        for a, b, c in graph.get("relationships", [])
    )

    attributes = set(
        (norm(a), norm(b), c)
        for a, b, c in graph.get("attributes", [])
    )

    graph["entities"] = list(entities)
    graph["relationships"] = [list(r) for r in relationships]
    graph["attributes"] = [list(a) for a in attributes]

    return graph


# 🔹 Merge batches
def merge_graphs(all_graphs):
    final = {"entities": [], "relationships": [], "attributes": []}

    for g in all_graphs:
        final["entities"].extend(g.get("entities", []))
        final["relationships"].extend(g.get("relationships", []))
        final["attributes"].extend(g.get("attributes", []))

    return final


# 🔥 MAIN PROCESS
def process_chunks(chunk_path, output_dir, batch_size=10):

    with open(chunk_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    os.makedirs(output_dir, exist_ok=True)

    neo4j = Neo4jHandler()
    all_graphs = []

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        print(f"\n🚀 Processing batch {i//batch_size}")

        # ✅ BEST INPUT TO LLM
        text = json.dumps(batch, indent=2)

        graph = extract_graph(text)
        graph = normalize_graph(graph)

        all_graphs.append(graph)

    # 🔹 Merge + Deduplicate
    final_graph = merge_graphs(all_graphs)
    final_graph = deduplicate_graph(final_graph)

    # 🔹 Save output
    output_file = os.path.join(output_dir, "final_graph.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(final_graph, f, indent=2)

    print(f"\n💾 Saved: {output_file}")

    # 🔹 Insert into Neo4j
    neo4j.insert_graph_data(final_graph)
    neo4j.close()

    print("✅ Done")

    return final_graph