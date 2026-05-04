
import json
import os
from chunk_to_graph import chunks_to_graph_data
from neo4j_handler import Neo4jHandler

def process_chunks(chunk_path, output_dir, batch_size=20):
    """
    Process chunks using the reliable rule-based approach.
    batch_size is kept for compatibility and future-proofing, 
    but not really needed for performance.
    """

    print(f" Loading chunks from: {chunk_path}")
    with open(chunk_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    os.makedirs(output_dir, exist_ok=True)

    print(f" Processing {len(chunks)} chunks using rule-based transformer...")

    # Process in batches
    all_graphs = []
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        print(f"   Processing batch {i//batch_size + 1} ({len(batch)} chunks)")

        graph_data = chunks_to_graph_data(batch)   # rule-based
        all_graphs.append(graph_data)

    # Merge all batches
    final_graph = {
        "entities": [],
        "relationships": [],
        "attributes": []
    }

    for g in all_graphs:
        final_graph["entities"].extend(g.get("entities", []))
        final_graph["relationships"].extend(g.get("relationships", []))
        final_graph["attributes"].extend(g.get("attributes", []))

    # Remove duplicates (simple way)
    final_graph["entities"] = list(dict.fromkeys(final_graph["entities"]))

    print(f" Final Stats - Entities: {len(final_graph['entities'])} | "
          f"Relationships: {len(final_graph['relationships'])} | "
          f"Attributes: {len(final_graph['attributes'])}")

    # Save final graph
    output_file = os.path.join(output_dir, "final_graph.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(final_graph, f, indent=2)
    print(f" Saved final graph: {output_file}")

    # Insert into Neo4j
    print("  Inserting into Neo4j...")
    neo4j = Neo4jHandler()
    neo4j.insert_graph_data(final_graph)
    neo4j.close()

    print(" Rule-based processing completed successfully!")
    return final_graph