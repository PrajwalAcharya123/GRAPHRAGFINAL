# # # src/neo4j_handler.py
# # from neo4j import GraphDatabase
# # import os
# # import re
# # from dotenv import load_dotenv
# # load_dotenv()

# # class Neo4jHandler:
# #     def __init__(self):
# #         self.driver = GraphDatabase.driver(
# #             os.getenv("NEO4J_URI"),
# #             auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
# #         )
# #         print("✅ Connected to Neo4j")

# #     def close(self):
# #         self.driver.close()

# #     # 🔥 CLEAN RELATION / ATTRIBUTE TYPE
# #     def clean_rel_type(self, text):
# #         """
# #         Convert text into valid Neo4j relationship type:
# #         - Uppercase
# #         - Replace non-alphanumeric with _
# #         """
# #         return re.sub(r'[^A-Z0-9]', '_', text.upper())

# #     # 🔹 Insert full graph
# #     def insert_graph_data(self, graph_data):
# #         entities = graph_data.get("entities", [])
# #         relationships = graph_data.get("relationships", [])
# #         attributes = graph_data.get("attributes", [])

# #         # 🔹 Insert entities
# #         for e in entities:
# #             with self.driver.session() as session:
# #                 session.run(
# #                     "MERGE (e:Entity {name: $name})",
# #                     name=e
# #                 )

# #         # 🔹 Insert relationships
# #         for rel in relationships:
# #             if len(rel) == 3:
# #                 self.insert_relationship(rel[0], rel[1], rel[2])

# #         # 🔹 Insert attributes
# #         for attr in attributes:
# #             if len(attr) == 3:
# #                 self.insert_attribute(attr[0], attr[1], attr[2])

# #     # 🔹 Relationship
# #     def insert_relationship(self, e1, rel, e2):
# #         rel_clean = self.clean_rel_type(rel)

# #         # log_path = "src/output/neo4j_log.txt"
# #         # os.makedirs("src/output", exist_ok=True)
# #         BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# #         OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# #         os.makedirs(OUTPUT_DIR, exist_ok=True)

# #         log_path = os.path.join(OUTPUT_DIR, "neo4j_log.txt")
# #         with open(log_path, "a", encoding="utf-8") as f:
# #             f.write(f"{e1} -[{rel_clean}]-> {e2}\n")

# #         print(f"➡️ REL: {e1} -[{rel_clean}]-> {e2}")

# #         query = f"""
# #         MERGE (a:Entity {{name: $e1}})
# #         MERGE (b:Entity {{name: $e2}})
# #         MERGE (a)-[:{rel_clean}]->(b)
# #         """

# #         with self.driver.session() as session:
# #             session.run(query, e1=e1, e2=e2)

# #     # 🔹 Attribute
# #     def insert_attribute(self, entity, key, value):
# #         key_clean = self.clean_rel_type(key)

# #         log_path = "src/output/neo4j_log.txt"
# #         os.makedirs("src/output", exist_ok=True)

# #         with open(log_path, "a", encoding="utf-8") as f:
# #             f.write(f"{entity} -[{key_clean}]-> {value}\n")

# #         print(f"➡️ ATTR: {entity} -[{key_clean}]-> {value}")

# #         query = f"""
# #         MERGE (e:Entity {{name: $entity}})
# #         MERGE (v:Value {{name: $value}})
# #         MERGE (e)-[:{key_clean}]->(v)
# #         """

# #         with self.driver.session() as session:
# #             session.run(query, entity=entity, value=value)

# #     def run_query(self, cypher_query):
# #         try:
# #             with self.driver.session() as session:
# #                 result = session.run(cypher_query)
# #                 return [record.data() for record in result]
# #         except Exception as e:
# #             print("❌ Query Error:", e)
# #             return []




from neo4j import GraphDatabase
import os
import re
from dotenv import load_dotenv

load_dotenv()

class Neo4jHandler:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI"),
            auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
        )
        print("✅ Connected to Neo4j")

        # output dir for logs
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.output_dir = os.path.join(self.base_dir, "output")
        os.makedirs(self.output_dir, exist_ok=True)
        self.log_path = os.path.join(self.output_dir, "neo4j_log.txt")

    def close(self):
        self.driver.close()

    # 🔹 Clean relationship/attribute name
    def clean_rel_type(self, text):
        return re.sub(r'[^A-Z0-9]', '_', text.upper())

    # 🔹 Insert full graph
    def insert_graph_data(self, graph_data):
        entities = graph_data.get("entities", [])
        relationships = graph_data.get("relationships", [])
        attributes = graph_data.get("attributes", [])

        with self.driver.session() as session:

            # 🔹 Nodes
            for e in entities:
                session.run(
                    "MERGE (n:Entity {name: $name})",
                    name=e
                )

            # 🔹 Relationships
            for e1, rel, e2 in relationships:
                rel_clean = self.clean_rel_type(rel)

                session.run(f"""
                    MERGE (a:Entity {{name: $e1}})
                    MERGE (b:Entity {{name: $e2}})
                    MERGE (a)-[:{rel_clean}]->(b)
                """, e1=e1, e2=e2)

                with open(self.log_path, "a", encoding="utf-8") as f:
                    f.write(f"{e1} -[{rel_clean}]-> {e2}\n")

            # 🔹 Attributes
            for entity, key, value in attributes:
                key_clean = self.clean_rel_type(key)

                session.run(f"""
                    MERGE (e:Entity {{name: $entity}})
                    MERGE (v:Value {{name: $value}})
                    MERGE (e)-[:{key_clean}]->(v)
                """, entity=entity, value=value)

                with open(self.log_path, "a", encoding="utf-8") as f:
                    f.write(f"{entity} -[{key_clean}]-> {value}\n")

        print("✅ Data inserted into Neo4j")

    def run_query(self, query):
        with self.driver.session() as session:
            result = session.run(query)
            return [r.data() for r in result]
        







# # src/neo4j_handler.py
# from neo4j import GraphDatabase
# import os
# import re
# from dotenv import load_dotenv
# from typing import Dict, List, Any

# load_dotenv()

# class Neo4jHandler:
#     def __init__(self):
#         self.driver = GraphDatabase.driver(
#             os.getenv("NEO4J_URI"),
#             auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
#         )
#         self.base_dir = os.path.dirname(os.path.abspath(__file__))
#         self.output_dir = os.path.join(self.base_dir, "output")
#         os.makedirs(self.output_dir, exist_ok=True)
#         self.log_path = os.path.join(self.output_dir, "neo4j_log.txt")

#         print("✅ Connected to Neo4j")

#     def close(self):
#         self.driver.close()

#     # ====================== CLEANERS ======================
#     def clean_label(self, text: str) -> str:
#         """Clean node labels"""
#         text = re.sub(r'[^A-Z0-9_]', '', text.upper().replace(' ', '_'))
#         return text if text else "UNKNOWN"

#     def clean_rel_type(self, text: str) -> str:
#         """Clean relationship types (must be uppercase, no spaces)"""
#         text = re.sub(r'[^A-Z0-9_]', '_', text.upper())
#         return text.strip('_') or "RELATED_TO"

#     # ====================== MAIN INSERT ======================
#     def insert_graph_data(self, graph_data: Dict):
#         entities = graph_data.get("entities", [])
#         relationships = graph_data.get("relationships", [])
#         attributes = graph_data.get("attributes", [])

#         with self.driver.session() as session:
#             # 1. Create all Entities as :Entity nodes with proper properties
#             for entity_name in entities:
#                 session.run("""
#                     MERGE (e:Entity {name: $name})
#                 """, name=entity_name)

#             # 2. Create Relationships (much cleaner)
#             for e1, rel_type, e2 in relationships:
#                 if not all([e1, rel_type, e2]):
#                     continue
                    
#                 rel_clean = self.clean_rel_type(rel_type)

#                 session.run(f"""
#                     MERGE (a:Entity {{name: $e1}})
#                     MERGE (b:Entity {{name: $e2}})
#                     MERGE (a)-[:`{rel_clean}`]->(b)
#                 """, e1=e1, e2=e2)

#                 self._log(f"REL: {e1} -[{rel_clean}]-> {e2}")

#             # 3. Add Attributes as PROPERTIES (Better than creating Value nodes)
#             for entity_name, key, value in attributes:
#                 if not all([entity_name, key, value is not None]):
#                     continue

#                 key_clean = self.clean_rel_type(key)
#                 safe_value = str(value).replace("'", "\\'")

#                 session.run(f"""
#                     MATCH (e:Entity {{name: $entity}})
#                     SET e.`{key_clean}` = $value
#                 """, entity=entity_name, value=safe_value)

#                 self._log(f"ATTR: {entity_name}.{key_clean} = {value}")

#         print(f"✅ Inserted {len(entities)} entities, "
#               f"{len(relationships)} relationships, "
#               f"{len(attributes)} attributes into Neo4j")

#     # ====================== HELPER ======================
#     def _log(self, message: str):
#         with open(self.log_path, "a", encoding="utf-8") as f:
#             f.write(f"{message}\n")
#         print(f"   {message}")

#     # ====================== QUERY ======================
#     def run_query(self, cypher_query: str):
#         try:
#             with self.driver.session() as session:
#                 result = session.run(cypher_query)
#                 return [record.data() for record in result]
#         except Exception as e:
#             print(f"❌ Neo4j Query Error: {e}")
#             return []

#     def clear_database(self):
#         """Use with caution - clears everything"""
#         with self.driver.session() as session:
#             session.run("MATCH (n) DETACH DELETE n")
#         print("🗑️ Database cleared")












# # src/neo4j_handler.py
# from neo4j import GraphDatabase
# import os
# import re
# from dotenv import load_dotenv
# from typing import Dict

# load_dotenv()

# class Neo4jHandler:
#     def __init__(self):
#         self.driver = GraphDatabase.driver(
#             os.getenv("NEO4J_URI"),
#             auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
#         )
#         self.base_dir = os.path.dirname(os.path.abspath(__file__))
#         self.output_dir = os.path.join(self.base_dir, "output")
#         os.makedirs(self.output_dir, exist_ok=True)
#         self.log_path = os.path.join(self.output_dir, "neo4j_log.txt")

#         # ✅ Create index once on startup for fast MERGE lookups
#         self._create_indexes()
#         print("✅ Connected to Neo4j")

#     def close(self):
#         self.driver.close()

#     # ====================== INDEXES ======================
#     def _create_indexes(self):
#         """Create indexes for fast MERGE and lookup"""
#         with self.driver.session() as session:
#             session.run("""
#                 CREATE INDEX entity_name_index IF NOT EXISTS
#                 FOR (e:Entity) ON (e.name)
#             """)

#     # ====================== CLEANERS ======================
#     def clean_rel_type(self, text: str) -> str:
#         """
#         Relationship types must be:
#         - UPPERCASE
#         - No spaces (use underscore)
#         - No special characters
#         """
#         text = re.sub(r'[^A-Z0-9_]', '_', text.upper().replace(' ', '_'))
#         text = re.sub(r'_+', '_', text)          # collapse multiple underscores
#         return text.strip('_') or "RELATED_TO"

#     def clean_property_key(self, text: str) -> str:
#         """
#         Property keys:
#         - lowercase with underscores
#         - no special characters
#         """
#         text = re.sub(r'[^a-z0-9_]', '_', text.lower().replace(' ', '_'))
#         text = re.sub(r'_+', '_', text)
#         return text.strip('_') or "value"

#     # ====================== MAIN INSERT ======================
#     def insert_graph_data(self, graph_data: Dict):
#         entities      = graph_data.get("entities", [])
#         relationships = graph_data.get("relationships", [])
#         attributes    = graph_data.get("attributes", [])

#         # ✅ Filter out any bad data before touching Neo4j
#         valid_entities = [
#             e for e in entities
#             if isinstance(e, str) and e.strip()
#         ]

#         valid_relationships = [
#             r for r in relationships
#             if isinstance(r, (list, tuple))
#             and len(r) == 3
#             and all(isinstance(x, str) and x.strip() for x in r)
#         ]

#         valid_attributes = [
#             a for a in attributes
#             if isinstance(a, (list, tuple))
#             and len(a) == 3
#             and isinstance(a[0], str) and a[0].strip()
#             and isinstance(a[1], str) and a[1].strip()
#             and a[2] is not None
#         ]

#         with self.driver.session() as session:

#             # --------------------------------------------------
#             # STEP 1: Batch insert all entities
#             # --------------------------------------------------
#             if valid_entities:
#                 session.run("""
#                     UNWIND $names AS name
#                     MERGE (e:Entity {name: name})
#                 """, names=valid_entities)
#                 print(f"✅ Entities inserted: {len(valid_entities)}")

#             # --------------------------------------------------
#             # STEP 2: Insert relationships
#             # Dynamic rel types can't use UNWIND cleanly,
#             # so we group by rel_type and batch per type
#             # --------------------------------------------------
#             rel_groups: dict = {}
#             for e1, rel_type, e2 in valid_relationships:
#                 rel_clean = self.clean_rel_type(rel_type)
#                 rel_groups.setdefault(rel_clean, []).append({
#                     "e1": e1.strip(),
#                     "e2": e2.strip()
#                 })

#             for rel_type, pairs in rel_groups.items():
#                 session.run(f"""
#                     UNWIND $pairs AS pair
#                     MERGE (a:Entity {{name: pair.e1}})
#                     MERGE (b:Entity {{name: pair.e2}})
#                     MERGE (a)-[:`{rel_type}`]->(b)
#                 """, pairs=pairs)
#                 self._log(f"REL [{rel_type}] × {len(pairs)} pairs")

#             print(f"✅ Relationship types inserted: {len(rel_groups)} "
#                   f"| Total pairs: {len(valid_relationships)}")

#             # --------------------------------------------------
#             # STEP 3: Batch insert attributes as node properties
#             # Group by entity so we SET all props in one query
#             # --------------------------------------------------
#             attr_groups: dict = {}
#             for entity_name, key, value in valid_attributes:
#                 key_clean = self.clean_property_key(key)
#                 attr_groups.setdefault(entity_name.strip(), {})[key_clean] = str(value)

#             if attr_groups:
#                 # Build list of {entity, props} dicts
#                 attr_list = [
#                     {"entity": entity, "props": props}
#                     for entity, props in attr_groups.items()
#                 ]
#                 session.run("""
#                     UNWIND $items AS item
#                     MERGE (e:Entity {name: item.entity})
#                     SET e += item.props
#                 """, items=attr_list)
#                 self._log(f"ATTR: {len(attr_list)} entities updated with properties")

#             print(f"✅ Attributes inserted: {len(valid_attributes)} "
#                   f"across {len(attr_groups)} entities")

#         print(f"\n📊 Final Summary:")
#         print(f"   Entities     : {len(valid_entities)}")
#         print(f"   Relationships: {len(valid_relationships)}")
#         print(f"   Attributes   : {len(valid_attributes)}")

#     # ====================== HELPER ======================
#     def _log(self, message: str):
#         with open(self.log_path, "a", encoding="utf-8") as f:
#             f.write(f"{message}\n")
#         print(f"   {message}")

#     # ====================== QUERY ======================
#     def run_query(self, cypher_query: str):
#         try:
#             with self.driver.session() as session:
#                 result = session.run(cypher_query)
#                 return [record.data() for record in result]
#         except Exception as e:
#             print(f"❌ Neo4j Query Error: {e}")
#             return []

#     def clear_database(self):
#         """Use with caution - clears everything"""
#         with self.driver.session() as session:
#             session.run("MATCH (n) DETACH DELETE n")
#         print("🗑️ Database cleared")