# from importlib.resources import path
# import json
# import os
# from extractor import extract_graph, chunk_to_text
# from neo4j_handler import Neo4jHandler

# # 🔹 Normalize LLM output
# def normalize_graph(graph):
#     rels, attrs = [], []

#     for r in graph.get("relationships", []):
#         if isinstance(r, list) and len(r) == 3:
#             rels.append(r)
#         elif isinstance(r, dict):
#             if r.get("entity1") and r.get("type") and r.get("entity2"):
#                 rels.append([r["entity1"], r["type"], r["entity2"]])

#     for a in graph.get("attributes", []):
#         if isinstance(a, list) and len(a) == 3:
#             attrs.append(a)
#         elif isinstance(a, dict):
#             if a.get("entity") and a.get("attribute") and a.get("value"):
#                 attrs.append([a["entity"], a["attribute"], a["value"]])

#     graph["relationships"] = rels
#     graph["attributes"] = attrs
#     return graph


# # 🔹 Normalize + Deduplicate
# def deduplicate_graph(graph):
#     def norm(x): return x.strip().lower()

#     entities = set(norm(e) for e in graph.get("entities", []))

#     relationships = set(
#         (norm(a), norm(b), norm(c))
#         for a, b, c in graph.get("relationships", [])
#     )

#     attributes = set(
#         (norm(a), norm(b), c)
#         for a, b, c in graph.get("attributes", [])
#     )

#     graph["entities"] = list(entities)
#     graph["relationships"] = [list(r) for r in relationships]
#     graph["attributes"] = [list(a) for a in attributes]

#     return graph


# # 🔹 Merge batches
# def merge_graphs(all_graphs):
#     final = {"entities": [], "relationships": [], "attributes": []}

#     for g in all_graphs:
#         final["entities"].extend(g.get("entities", []))
#         final["relationships"].extend(g.get("relationships", []))
#         final["attributes"].extend(g.get("attributes", []))

#     return final

# def process_chunks(chunk_path, output_dir, batch_size=10):

#     with open(chunk_path, "r", encoding="utf-8") as f:
#         chunks = json.load(f)

#     os.makedirs(output_dir, exist_ok=True)

#     neo4j = Neo4jHandler()
#     all_graphs = []

#     for i in range(0, len(chunks), batch_size):
#         batch = chunks[i:i + batch_size]
#         print(f"\n🚀 Processing batch {i//batch_size}")

#         # text = json.dumps(batch, indent=2)

#         # graph = extract_graph(text)
#         texts = [chunk_to_text(c) for c in batch]
#         text = "\n".join(texts)

#         graph = extract_graph(text)

#         print("this is graph output:", graph)

#         output_file = os.path.join(output_dir, "after_extractor.json")

#         with open(output_file, "w", encoding="utf-8") as f:
#             json.dump(graph, f, indent=2)

#         print(f"✅ Saved batch graph to: {output_file}")    

#         graph = normalize_graph(graph)
#         all_graphs.append(graph)

#     final_graph = merge_graphs(all_graphs)
#     final_graph = deduplicate_graph(final_graph)

#     output_file = os.path.join(output_dir, "final_graph.json")
#     with open(output_file, "w", encoding="utf-8") as f:
#         json.dump(final_graph, f, indent=2)

#     print(f"\n💾 Saved: {output_file}")

#     # 🔹 Insert into Neo4j
#     inserted = neo4j.insert_graph_data(final_graph)

#     print("\n🔍 Inserted Data:\n")
#     print(json.dumps(inserted, indent=2))

#     with open("neo4j_inserted_output.json", "w", encoding="utf-8") as f:
#         json.dump(inserted, f, indent=2)

#     print("📦 Saved to neo4j_inserted_output.json")

#     neo4j.close()
#     print("✅ Done")

#     return final_graph




















import json
import os
from extractor import extract_graph, chunk_to_text
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


# 🔹 Deduplicate (preserve original values)
def deduplicate_graph(graph):
    seen_entities = set()
    seen_relationships = set()
    seen_attributes = set()

    entities = []
    relationships = []
    attributes = []

    for e in graph.get("entities", []):
        key = e.strip().lower()
        if key not in seen_entities:
            seen_entities.add(key)
            entities.append(e)

    for a, b, c in graph.get("relationships", []):
        key = (a.strip().lower(), b.strip().lower(), c.strip().lower())
        if key not in seen_relationships:
            seen_relationships.add(key)
            relationships.append([a, b, c])

    for a, b, c in graph.get("attributes", []):
        key = (a.strip().lower(), b.strip().lower(), str(c))
        if key not in seen_attributes:
            seen_attributes.add(key)
            attributes.append([a, b, c])

    graph["entities"] = entities
    graph["relationships"] = relationships
    graph["attributes"] = attributes

    return graph


# 🔹 Merge batches
def merge_graphs(all_graphs):
    final = {"entities": [], "relationships": [], "attributes": []}

    for g in all_graphs:
        final["entities"].extend(g.get("entities", []))
        final["relationships"].extend(g.get("relationships", []))
        final["attributes"].extend(g.get("attributes", []))

    return final


# 🔥 MAIN PIPELINE
def process_chunks(chunk_path, output_dir, batch_size=10):

    with open(chunk_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    os.makedirs(output_dir, exist_ok=True)

    neo4j = Neo4jHandler()
    all_graphs = []

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        print(f"\n🚀 Processing batch {i//batch_size}")

        # 🔹 Convert chunks → text
        texts = [chunk_to_text(c) for c in batch if chunk_to_text(c).strip()]
        if not texts:
            print("⚠️ Skipping empty batch")
            continue

        text = "\n".join(texts)

        # 🔹 LLM extraction
        try:
            graph = extract_graph(text)
        except Exception as e:
            print("❌ LLM extraction failed:", e)
            continue

        print("🔍 Graph output:", graph)

        # 🔹 Save per batch (IMPORTANT FIX)
        batch_file = os.path.join(output_dir, f"batch_{i//batch_size}.json")
        with open(batch_file, "w", encoding="utf-8") as f:
            json.dump(graph, f, indent=2)

        print(f"✅ Saved batch graph to: {batch_file}")

        graph = normalize_graph(graph)
        all_graphs.append(graph)

    # 🔹 Merge + deduplicate
    final_graph = merge_graphs(all_graphs)
    final_graph = deduplicate_graph(final_graph)

    # 🔹 Save final graph
    final_file = os.path.join(output_dir, "final_graph.json")
    with open(final_file, "w", encoding="utf-8") as f:
        json.dump(final_graph, f, indent=2)

    print(f"\n💾 Saved: {final_file}")

    # 🔹 Insert into Neo4j
    inserted = neo4j.insert_graph_data(final_graph)

    print("\n🔍 Inserted Data:\n")
    print(json.dumps(inserted, indent=2))

    # 🔹 Save inserted output
    insert_file = os.path.join(output_dir, "neo4j_inserted_output.json")
    with open(insert_file, "w", encoding="utf-8") as f:
        json.dump(inserted, f, indent=2)

    print(f"📦 Saved to {insert_file}")

    neo4j.close()
    print("✅ Done")

    return final_graph