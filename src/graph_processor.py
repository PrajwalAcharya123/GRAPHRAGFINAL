from importlib.resources import path
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


# # 🔥 MAIN PROCESS
# def process_chunks(chunk_path, output_dir, batch_size=10):

#     with open(chunk_path, "r", encoding="utf-8") as f:
#         chunks = json.load(f)

#     os.makedirs(output_dir, exist_ok=True)

#     neo4j = Neo4jHandler()
#     all_graphs = []

#     for i in range(0, len(chunks), batch_size):
#         batch = chunks[i:i + batch_size]
#         print(f"\n🚀 Processing batch {i//batch_size}")

#         # ✅ BEST INPUT TO LLM
#         text = json.dumps(batch, indent=2)

#         graph = extract_graph(text)
#         print(graph)
#         # Define output file path
#         output_file = os.path.join(output_dir, "after_extractor.json")

#         # Write graph to JSON file
#         with open(output_file, "w", encoding="utf-8") as f:
#          json.dump(graph, f, indent=2)
#         print(f"✅ Saved batch graph to: {output_file}")    
#         graph = normalize_graph(graph)

#         all_graphs.append(graph)

#     # 🔹 Merge + Deduplicate
#     final_graph = merge_graphs(all_graphs)
#     final_graph = deduplicate_graph(final_graph)

#     # 🔹 Save output
#     output_file = os.path.join(output_dir, "final_graph.json")
#     with open(output_file, "w", encoding="utf-8") as f:
#         json.dump(final_graph, f, indent=2)

#     print(f"\n💾 Saved: {output_file}")

#     # # 🔹 Insert into Neo4j
#     # neo4j.insert_graph_data(final_graph)
#     # neo4j.close()

#     # print("✅ Done")

#     # return final_graph
#     # 🔹 Insert into Neo4j
#     inserted = neo4j.insert_graph_data(final_graph)

#     # 🔹 Print in terminal
#     import json
#     print("\n🔍 Inserted Data:\n")
#     print(json.dumps(inserted, indent=2))

#     # 🔹 Save to separate file
#     with open("neo4j_inserted_output.json", "w", encoding="utf-8") as f:
#         json.dump(inserted, f, indent=2)

#     print("📦 Saved to neo4j_inserted_output.json")

#     neo4j.close()

#     print("✅ Done")

#     return final_graph




import json   # ✅ MUST BE AT TOP
import os

def process_chunks(chunk_path, output_dir, batch_size=10):

    with open(chunk_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    os.makedirs(output_dir, exist_ok=True)

    neo4j = Neo4jHandler()
    all_graphs = []

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        print(f"\n🚀 Processing batch {i//batch_size}")

        text = json.dumps(batch, indent=2)

        graph = extract_graph(text)
        print("this is graph output:", graph)

        output_file = os.path.join(output_dir, "after_extractor.json")

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(graph, f, indent=2)

        print(f"✅ Saved batch graph to: {output_file}")    

        graph = normalize_graph(graph)
        all_graphs.append(graph)

    final_graph = merge_graphs(all_graphs)
    final_graph = deduplicate_graph(final_graph)

    output_file = os.path.join(output_dir, "final_graph.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(final_graph, f, indent=2)

    print(f"\n💾 Saved: {output_file}")

    # 🔹 Insert into Neo4j
    inserted = neo4j.insert_graph_data(final_graph)

    print("\n🔍 Inserted Data:\n")
    print(json.dumps(inserted, indent=2))

    with open("neo4j_inserted_output.json", "w", encoding="utf-8") as f:
        json.dump(inserted, f, indent=2)

    print("📦 Saved to neo4j_inserted_output.json")

    neo4j.close()
    print("✅ Done")

    return final_graph




# import json
# import os
# from extractor import extract_graph  # Keep if you want fallback LLM extraction
# from neo4j_handler import Neo4jHandler
# from typing import List, Dict, Any

# # ====================== DOMAIN-SPECIFIC MAPPING ======================

# def create_sbc_graph_from_chunks(chunks: List[Dict]) -> Dict:
#     """Smart, rule-based graph construction for SBC documents"""
#     entities = set()
#     relationships = []
#     attributes = []

#     for chunk in chunks:
#         chunk_type = chunk.get("type")
#         chunk_id = chunk.get("chunk_id")

#         if chunk_type == "plan_metadata":
#             entities.add("HealthPlan")
#             attributes.append(["HealthPlan", "coverage_for", "Family"])
#             attributes.append(["HealthPlan", "document_type", "Summary of Benefits and Coverage (SBC)"])

#         elif chunk_type == "important_question":
#             question = chunk.get("question", "").strip()
#             answer = chunk.get("answer", "").strip()
#             why = chunk.get("why_it_matters", "").strip()

#             if not question:
#                 continue

#             q_lower = question.lower()

#             # Create main entity
#             if "out-of-pocket limit" in q_lower or "oop limit" in q_lower:
#                 entity_name = "OutOfPocketLimit"
#                 entities.add(entity_name)
#                 attributes.append([entity_name, "value", answer])
#                 attributes.append([entity_name, "description", why])

#                 # Special handling for exclusions
#                 if "not included" in q_lower or "not included in the out-of-pocket" in q_lower:
#                     exclusions = [item.strip() for item in answer.split(",") if item.strip()]
#                     for excl in exclusions:
#                         excl_entity = f"Exclusion_{excl.replace(' ', '_')[:50]}"
#                         entities.add(excl_entity)
#                         relationships.append([entity_name, "EXCLUDES", excl_entity])
#                         attributes.append([excl_entity, "name", excl])

#             elif "overall deductible" in q_lower:
#                 entity_name = "OverallDeductible"
#                 entities.add(entity_name)
#                 attributes.append([entity_name, "value", answer])
#                 attributes.append([entity_name, "description", why])

#             elif "other deductibles" in q_lower:
#                 entity_name = "SpecificDeductible"
#                 entities.add(entity_name)
#                 attributes.append([entity_name, "value", answer])

#             else:
#                 entity_name = f"Question_{chunk_id}"
#                 entities.add(entity_name)
#                 attributes.append([entity_name, "question", question])
#                 attributes.append([entity_name, "answer", answer])

#         elif chunk_type == "benefit_service":
#             service = chunk.get("service", "").strip()
#             if not service:
#                 continue

#             entities.add("BenefitService")
#             service_node = f"Service_{service.replace(' ', '_')[:60]}"
#             entities.add(service_node)

#             attributes.append([service_node, "name", service])
#             attributes.append([service_node, "medical_event", chunk.get("medical_event", "")])
#             attributes.append([service_node, "network_cost", chunk.get("network_cost", "")])
#             attributes.append([service_node, "out_of_network_cost", chunk.get("out_of_network_cost", "")])
#             attributes.append([service_node, "limitations", chunk.get("limitations", "")])

#             # Important relationships
#             relationships.append(["HealthPlan", "OFFERS", service_node])
            
#             if chunk.get("requires_preauth"):
#                 relationships.append([service_node, "REQUIRES", "Preauthorization"])

#         elif chunk_type == "excluded_service":
#             service = chunk.get("service", "").strip()
#             if service:
#                 excl_node = f"ExcludedService_{service.replace(' ', '_')[:50]}"
#                 entities.add(excl_node)
#                 attributes.append([excl_node, "name", service])
#                 relationships.append(["HealthPlan", "EXCLUDES", excl_node])

#         elif chunk_type == "coverage_example":
#             name = chunk.get("name", "")
#             example_node = f"Example_{name.replace(' ', '_')[:40]}"
#             entities.add(example_node)
#             attributes.append([example_node, "name", name])
#             attributes.append([example_node, "total_cost", chunk.get("total_cost", "")])
#             attributes.append([example_node, "patient_pays", chunk.get("patient_total", "")])

#             relationships.append(["HealthPlan", "HAS_EXAMPLE", example_node])

#     # Final graph
#     return {
#         "entities": list(entities),
#         "relationships": relationships,
#         "attributes": attributes
#     }


# # ====================== IMPROVED MAIN PROCESS ======================

# def process_chunks(chunk_path: str, output_dir: str):

#     with open(chunk_path, "r", encoding="utf-8") as f:
#         chunks = json.load(f)

#     os.makedirs(output_dir, exist_ok=True)

#     print(f"Loaded {len(chunks)} chunks")

#     # 1. Smart Rule-based Graph Construction (Best quality)
#     print("🔨 Building smart SBC graph...")
#     graph = create_sbc_graph_from_chunks(chunks)

#     # 2. Optional: LLM fallback for complex chunks (if needed)
#     # graph = enhance_with_llm(graph, chunks)

#     # Save
#     output_file = os.path.join(output_dir, "final_graph.json")
#     with open(output_file, "w", encoding="utf-8") as f:
#         json.dump(graph, f, indent=2)

#     print(f"💾 Saved graph to {output_file}")
#     print(f"   Entities: {len(graph['entities'])}")
#     print(f"   Relationships: {len(graph['relationships'])}")
#     print(f"   Attributes: {len(graph['attributes'])}")

#     # 3. Insert into Neo4j with smart Cypher
#     neo4j = Neo4jHandler()
#     neo4j.insert_graph_data(graph)   # Make sure this method is updated too
#     neo4j.close()

#     print("✅ Process completed successfully!")
#     return graph























# import json
# import os
# from neo4j_handler import Neo4jHandler
# from extractor import extract_graph   # 🔥 LLM call (MANDATORY)


# # ======================
# # RULE-BASED GRAPH (PRIMARY)
# # ======================

# def create_rule_based_graph(chunks):
#     entities = set()
#     relationships = []
#     attributes = []

#     for chunk in chunks:
#         chunk_type = chunk.get("type")

#         if chunk_type == "plan_metadata":
#             entities.add("HealthPlan")
#             attributes.append(["HealthPlan", "document_type", "SBC"])

#         elif chunk_type == "important_question":
#             question = chunk.get("question", "").lower()
#             answer = chunk.get("answer", "")

#             if "out-of-pocket" in question:
#                 entities.add("OutOfPocketLimit")
#                 attributes.append(["OutOfPocketLimit", "value", answer])

#             elif "deductible" in question:
#                 entities.add("Deductible")
#                 attributes.append(["Deductible", "value", answer])

#         elif chunk_type == "benefit_service":
#             service = chunk.get("service", "")
#             if service:
#                 node = f"Service_{service.replace(' ', '_')[:50]}"
#                 entities.add(node)
#                 attributes.append([node, "name", service])
#                 relationships.append(["HealthPlan", "OFFERS", node])

#     return {
#         "entities": list(entities),
#         "relationships": relationships,
#         "attributes": attributes
#     }


# # ======================
# # LLM ENHANCEMENT (MANDATORY)
# # ======================

# def enhance_with_llm(chunks):
#     text = json.dumps(chunks, indent=2)

#     try:
#         llm_graph = extract_graph(text)  # 🔥 MUST CALL LLM
#         return llm_graph
#     except Exception as e:
#         print("⚠️ LLM failed:", e)
#         return {"entities": [], "relationships": [], "attributes": []}


# # ======================
# # MERGE GRAPHS
# # ======================

# def merge_graphs(rule_graph, llm_graph):
#     final = {
#         "entities": set(),
#         "relationships": set(),
#         "attributes": set()
#     }

#     def normalize(x):
#         return x.strip()

#     # Rule-based
#     for e in rule_graph["entities"]:
#         final["entities"].add(normalize(e))

#     for r in rule_graph["relationships"]:
#         final["relationships"].add(tuple(map(normalize, r)))

#     for a in rule_graph["attributes"]:
#         final["attributes"].add((normalize(a[0]), normalize(a[1]), a[2]))

#     # LLM-based
#     for e in llm_graph.get("entities", []):
#         final["entities"].add(normalize(e))

#     for r in llm_graph.get("relationships", []):
#         if len(r) == 3:
#             final["relationships"].add(tuple(map(normalize, r)))

#     for a in llm_graph.get("attributes", []):
#         if len(a) == 3:
#             final["attributes"].add((normalize(a[0]), normalize(a[1]), a[2]))

#     return {
#         "entities": list(final["entities"]),
#         "relationships": [list(r) for r in final["relationships"]],
#         "attributes": [list(a) for a in final["attributes"]]
#     }


# # ======================
# # MAIN PROCESS
# # ======================



# def save_json(data, path):
#     os.makedirs(os.path.dirname(path), exist_ok=True)
#     with open(path, "w", encoding="utf-8") as f:
#         json.dump(data, f, indent=2)


# def process_chunks(chunk_path, output_dir):

#     with open(chunk_path, "r", encoding="utf-8") as f:
#         chunks = json.load(f)

#     os.makedirs(output_dir, exist_ok=True)

#     print(f"📦 Loaded {len(chunks)} chunks")

#     # 🔹 STEP 1: Rule-based
#     print("🔨 Building rule-based graph...")
#     rule_graph = create_rule_based_graph(chunks)

#     rule_path = os.path.join(output_dir, "rule_graph.json")
#     save_json(rule_graph, rule_path)
#     print(f"📁 Saved rule-based graph → {rule_path}")

#     # 🔹 STEP 2: LLM
#     print("🤖 Extracting with LLM...")
#     llm_graph = extract_graph(json.dumps(chunks, indent=2))

#     llm_path = os.path.join(output_dir, "llm_graph.json")
#     save_json(llm_graph, llm_path)
#     print(f"📁 Saved LLM graph → {llm_path}")

#     # 🔹 STEP 3: Merge
#     print("🔗 Merging graphs...")
#     final_graph = merge_graphs(rule_graph, llm_graph)

#     final_path = os.path.join(output_dir, "final_graph.json")
#     save_json(final_graph, final_path)
#     print(f"📁 Saved final graph → {final_path}")

#     # 🔹 STEP 4: Neo4j
#     neo4j = Neo4jHandler()
#     neo4j.insert_graph_data(final_graph)
#     neo4j.close()

#     print("✅ Done")

#     return final_graph



















# import json
# import os
# from neo4j_handler import Neo4jHandler
# from extractor import extract_graph


# # ======================
# # RULE-BASED GRAPH
# # ======================

# def create_rule_based_graph(chunks):
#     entities = set()
#     relationships = []
#     attributes = []

#     for chunk in chunks:
#         chunk_type = chunk.get("type")

#         if chunk_type == "plan_metadata":
#             entities.add("HealthPlan")
#             attributes.append(["HealthPlan", "document_type", "SBC"])

#         elif chunk_type == "important_question":
#             question = chunk.get("question", "").lower()
#             answer = chunk.get("answer", "")

#             if "out-of-pocket" in question:
#                 entities.add("OutOfPocketLimit")
#                 attributes.append(["OutOfPocketLimit", "value", answer])

#             elif "deductible" in question:
#                 entities.add("Deductible")
#                 attributes.append(["Deductible", "value", answer])

#         elif chunk_type == "benefit_service":
#             service = chunk.get("service", "")
#             if service:
#                 node = f"Service_{service.replace(' ', '_')[:50]}"
#                 entities.add(node)
#                 attributes.append([node, "name", service])
#                 relationships.append(["HealthPlan", "OFFERS", node])

#     return {
#         "entities": list(entities),
#         "relationships": relationships,
#         "attributes": attributes
#     }


# # ======================
# # FLATTEN LLM GRAPH
# # Convert tables + rules → entities/relationships/attributes
# # ======================

# def flatten_llm_graph(llm_graph):
#     """
#     Takes raw LLM output (which may have tables/rules)
#     and converts everything into the 3 GraphRAG primitives.
#     """
#     entities = list(llm_graph.get("entities", []))
#     relationships = list(llm_graph.get("relationships", []))
#     attributes = list(llm_graph.get("attributes", []))

#     # --- Flatten tables → entities + attributes + relationships ---
#     for table in llm_graph.get("tables", []):
#         if not isinstance(table, dict):
#             continue

#         service = table.get("service", "").strip()
#         if not service:
#             continue

#         # Service becomes an entity
#         entities.append(service)
#         relationships.append(["HealthPlan", "COVERS", service])

#         # Each column becomes an attribute
#         for key, value in table.items():
#             if key != "service" and value:
#                 attributes.append([service, key, str(value)])

#     # --- Flatten rules → relationships ---
#     for rule in llm_graph.get("rules", []):
#         if isinstance(rule, (list, tuple)) and len(rule) == 3:
#             relationships.append(list(rule))
#             # Also ensure both ends are registered as entities
#             entities.append(str(rule[0]))
#             entities.append(str(rule[2]))

#     return {
#         "entities": entities,
#         "relationships": relationships,
#         "attributes": attributes
#     }


# # ======================
# # MERGE GRAPHS
# # ======================

# def merge_graphs(rule_graph, llm_graph):
#     final = {
#         "entities": set(),
#         "relationships": set(),
#         "attributes": set()
#     }

#     def normalize(x):
#         return str(x).strip()

#     # --- Rule-based ---
#     for e in rule_graph.get("entities", []):
#         final["entities"].add(normalize(e))

#     for r in rule_graph.get("relationships", []):
#         if isinstance(r, (list, tuple)) and len(r) == 3:
#             final["relationships"].add(tuple(map(normalize, r)))

#     for a in rule_graph.get("attributes", []):
#         if isinstance(a, (list, tuple)) and len(a) == 3:
#             final["attributes"].add((normalize(a[0]), normalize(a[1]), normalize(a[2])))

#     # --- LLM-based (already flattened) ---
#     for e in llm_graph.get("entities", []):
#         final["entities"].add(normalize(e))

#     for r in llm_graph.get("relationships", []):
#         if isinstance(r, (list, tuple)) and len(r) == 3:
#             final["relationships"].add(tuple(map(normalize, r)))

#     for a in llm_graph.get("attributes", []):
#         if isinstance(a, (list, tuple)) and len(a) == 3:
#             final["attributes"].add((normalize(a[0]), normalize(a[1]), normalize(a[2])))

#     return {
#         "entities": list(final["entities"]),
#         "relationships": [list(r) for r in final["relationships"]],
#         "attributes": [list(a) for a in final["attributes"]]
#     }


# # ======================
# # SAVE HELPER
# # ======================

# def save_json(data, path):
#     os.makedirs(os.path.dirname(path), exist_ok=True)
#     with open(path, "w", encoding="utf-8") as f:
#         json.dump(data, f, indent=2)


# # ======================
# # MAIN PIPELINE
# # ======================

# def process_chunks(chunk_path, output_dir):

#     with open(chunk_path, "r", encoding="utf-8") as f:
#         chunks = json.load(f)

#     os.makedirs(output_dir, exist_ok=True)
#     print(f"📦 Loaded {len(chunks)} chunks")

#     # STEP 1: Rule-based graph
#     print("🔨 Building rule-based graph...")
#     rule_graph = create_rule_based_graph(chunks)
#     save_json(rule_graph, os.path.join(output_dir, "rule_graph.json"))
#     print(f"   Entities: {len(rule_graph['entities'])} | "
#           f"Relationships: {len(rule_graph['relationships'])} | "
#           f"Attributes: {len(rule_graph['attributes'])}")

#     # STEP 2: LLM graph (raw, may have tables/rules)
#     print("🤖 Extracting with LLM...")
#     raw_llm_graph = extract_graph(json.dumps(chunks, indent=2))
#     save_json(raw_llm_graph, os.path.join(output_dir, "llm_graph_raw.json"))

#     # STEP 3: Flatten tables/rules into entities/relationships/attributes
#     print("🔄 Flattening tables and rules...")
#     llm_graph = flatten_llm_graph(raw_llm_graph)
#     save_json(llm_graph, os.path.join(output_dir, "llm_graph.json"))
#     print(f"   Entities: {len(llm_graph['entities'])} | "
#           f"Relationships: {len(llm_graph['relationships'])} | "
#           f"Attributes: {len(llm_graph['attributes'])}")

#     # STEP 4: Merge both graphs
#     print("🔗 Merging graphs...")
#     final_graph = merge_graphs(rule_graph, llm_graph)
#     save_json(final_graph, os.path.join(output_dir, "final_graph.json"))
#     print(f"   ✅ Final → Entities: {len(final_graph['entities'])} | "
#           f"Relationships: {len(final_graph['relationships'])} | "
#           f"Attributes: {len(final_graph['attributes'])}")

#     # STEP 5: Insert into Neo4j
#     print("🗄️ Inserting into Neo4j...")
#     neo4j = Neo4jHandler()
#     neo4j.insert_graph_data(final_graph)
#     neo4j.close()

#     print("✅ Done")
#     return final_graph