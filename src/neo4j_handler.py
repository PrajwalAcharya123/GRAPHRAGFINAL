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




                                                                        # from neo4j import GraphDatabase
                                                                        # import os
                                                                        # import re
                                                                        # from dotenv import load_dotenv

                                                                        # load_dotenv()

                                                                        # class Neo4jHandler:
                                                                        #     def __init__(self):
                                                                        #         self.driver = GraphDatabase.driver(
                                                                        #             os.getenv("NEO4J_URI"),
                                                                        #             auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
                                                                        #         )
                                                                        #         print("✅ Connected to Neo4j")

                                                                        #         # output dir for logs
                                                                        #         self.base_dir = os.path.dirname(os.path.abspath(__file__))
                                                                        #         self.output_dir = os.path.join(self.base_dir, "output")
                                                                        #         os.makedirs(self.output_dir, exist_ok=True)
                                                                        #         self.log_path = os.path.join(self.output_dir, "neo4j_log.txt")

                                                                        #     def close(self):
                                                                        #         self.driver.close()

                                                                        #     # 🔹 Clean relationship/attribute name
                                                                        #     def clean_rel_type(self, text):
                                                                        #         return re.sub(r'[^A-Z0-9]', '_', text.upper())

                                                                        #     # 🔹 Insert full graph
                                                                        #     def insert_graph_data(self, graph_data):
                                                                        #         entities = graph_data.get("entities", [])
                                                                        #         relationships = graph_data.get("relationships", [])
                                                                        #         attributes = graph_data.get("attributes", [])

                                                                        #         with self.driver.session() as session:

                                                                        #             # 🔹 Nodes
                                                                        #             for e in entities:
                                                                        #                 session.run(
                                                                        #                     "MERGE (n:Entity {name: $name})",
                                                                        #                     name=e
                                                                        #                 )

                                                                        #             # 🔹 Relationships
                                                                        #             for e1, rel, e2 in relationships:
                                                                        #                 rel_clean = self.clean_rel_type(rel)

                                                                        #                 session.run(f"""
                                                                        #                     MERGE (a:Entity {{name: $e1}})
                                                                        #                     MERGE (b:Entity {{name: $e2}})
                                                                        #                     MERGE (a)-[:{rel_clean}]->(b)
                                                                        #                 """, e1=e1, e2=e2)

                                                                        #                 with open(self.log_path, "a", encoding="utf-8") as f:
                                                                        #                     f.write(f"{e1} -[{rel_clean}]-> {e2}\n")

                                                                        #             # 🔹 Attributes
                                                                        #             for entity, key, value in attributes:
                                                                        #                 key_clean = self.clean_rel_type(key)

                                                                        #                 session.run(f"""
                                                                        #                     MERGE (e:Entity {{name: $entity}})
                                                                        #                     MERGE (v:Value {{name: $value}})
                                                                        #                     MERGE (e)-[:{key_clean}]->(v)
                                                                        #                 """, entity=entity, value=value)

                                                                        #                 with open(self.log_path, "a", encoding="utf-8") as f:
                                                                        #                     f.write(f"{entity} -[{key_clean}]-> {value}\n")

                                                                        #         print("✅ Data inserted into Neo4j")

                                                                        #     def run_query(self, query):
                                                                        #         with self.driver.session() as session:
                                                                        #             result = session.run(query)
                                                                        #             return [r.data() for r in result]
                                                                                







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





from neo4j import GraphDatabase
import os
import re
import json
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
        text = text.upper().replace(" ", "_")
        return re.sub(r'[^A-Z0-9_]', '', text)

    # 🔹 Insert full graph
    def insert_graph_data(self, graph_data):
        entities = graph_data.get("entities", [])
        relationships = graph_data.get("relationships", [])
        attributes = graph_data.get("attributes", [])

        inserted_data = {
            "entities": [],
            "relationships": [],
            "attributes": []
        }

        try:
            with self.driver.session() as session:

                # 🔹 Nodes
                for e in entities:
                    session.run(
                        "MERGE (n:Entity {name: $name})",
                        name=e
                    )
                    inserted_data["entities"].append(e)

                # 🔹 Relationships
                for e1, rel, e2 in relationships:
                    rel_clean = self.clean_rel_type(rel)

                    session.run(f"""
                        MERGE (a:Entity {{name: $e1}})
                        MERGE (b:Entity {{name: $e2}})
                        MERGE (a)-[:{rel_clean}]->(b)
                    """, e1=e1, e2=e2)

                    inserted_data["relationships"].append({
                        "from": e1,
                        "relationship": rel_clean,
                        "to": e2
                    })

                    with open(self.log_path, "a", encoding="utf-8") as f:
                        f.write(json.dumps({
                            "from": e1,
                            "relationship": rel_clean,
                            "to": e2
                        }) + "\n")

                # 🔹 Attributes
                for entity, key, value in attributes:
                    key_clean = self.clean_rel_type(key)

                    session.run(f"""
                        MERGE (e:Entity {{name: $entity}})
                        MERGE (v:Value {{name: $value}})
                        MERGE (e)-[:{key_clean}]->(v)
                    """, entity=entity, value=value)

                    inserted_data["attributes"].append({
                        "entity": entity,
                        "key": key_clean,
                        "value": value
                    })

                    with open(self.log_path, "a", encoding="utf-8") as f:
                        f.write(json.dumps({
                            "entity": entity,
                            "key": key_clean,
                            "value": value
                        }) + "\n")

        except Exception as e:
            print("❌ Neo4j Insert Error:", e)

        print("✅ Data inserted into Neo4j")

        return inserted_data  # 🔥 NOW RETURNS DATA

    # 🔹 Run query
    def run_query(self, query):
        try:
            with self.driver.session() as session:
                result = session.run(query)
                return [r.data() for r in result]
        except Exception as e:
            print("❌ Query Error:", e)
            return []

    # 🔹 Debug: print sample graph
    def debug_print_graph(self, limit=20):
        query = f"""
        MATCH (a)-[r]->(b)
        RETURN a.name AS from, type(r) AS rel, b.name AS to
        LIMIT {limit}
        """
        data = self.run_query(query)

        print("\n🔍 Graph Preview:\n")
        for row in data:
            print(f"{row['from']} -[{row['rel']}]-> {row['to']}")

    # 🔹 Debug: count nodes + relationships
    def get_counts(self):
        nodes = self.run_query("MATCH (n) RETURN count(n) AS count")
        rels = self.run_query("MATCH ()-[r]->() RETURN count(r) AS count")

        node_count = nodes[0]["count"] if nodes else 0
        rel_count = rels[0]["count"] if rels else 0

        print(f"📊 Nodes: {node_count}, Relationships: {rel_count}")