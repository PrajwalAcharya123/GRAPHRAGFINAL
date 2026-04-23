# src/neo4j_handler.py
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

    def close(self):
        self.driver.close()

    # 🔥 CLEAN RELATION / ATTRIBUTE TYPE
    def clean_rel_type(self, text):
        """
        Convert text into valid Neo4j relationship type:
        - Uppercase
        - Replace non-alphanumeric with _
        """
        return re.sub(r'[^A-Z0-9]', '_', text.upper())

    # 🔹 Insert full graph
    def insert_graph_data(self, graph_data):
        entities = graph_data.get("entities", [])
        relationships = graph_data.get("relationships", [])
        attributes = graph_data.get("attributes", [])

        # 🔹 Insert entities
        for e in entities:
            with self.driver.session() as session:
                session.run(
                    "MERGE (e:Entity {name: $name})",
                    name=e
                )

        # 🔹 Insert relationships
        for rel in relationships:
            if len(rel) == 3:
                self.insert_relationship(rel[0], rel[1], rel[2])

        # 🔹 Insert attributes
        for attr in attributes:
            if len(attr) == 3:
                self.insert_attribute(attr[0], attr[1], attr[2])

    # 🔹 Relationship
    def insert_relationship(self, e1, rel, e2):
        rel_clean = self.clean_rel_type(rel)

        log_path = "src/output/neo4j_log.txt"
        os.makedirs("src/output", exist_ok=True)

        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"{e1} -[{rel_clean}]-> {e2}\n")

        print(f"➡️ REL: {e1} -[{rel_clean}]-> {e2}")

        query = f"""
        MERGE (a:Entity {{name: $e1}})
        MERGE (b:Entity {{name: $e2}})
        MERGE (a)-[:{rel_clean}]->(b)
        """

        with self.driver.session() as session:
            session.run(query, e1=e1, e2=e2)

    # 🔹 Attribute
    def insert_attribute(self, entity, key, value):
        key_clean = self.clean_rel_type(key)

        log_path = "src/output/neo4j_log.txt"
        os.makedirs("src/output", exist_ok=True)

        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"{entity} -[{key_clean}]-> {value}\n")

        print(f"➡️ ATTR: {entity} -[{key_clean}]-> {value}")

        query = f"""
        MERGE (e:Entity {{name: $entity}})
        MERGE (v:Value {{name: $value}})
        MERGE (e)-[:{key_clean}]->(v)
        """

        with self.driver.session() as session:
            session.run(query, entity=entity, value=value)

    def run_query(self, cypher_query):
        try:
            with self.driver.session() as session:
                result = session.run(cypher_query)
                return [record.data() for record in result]
        except Exception as e:
            print("❌ Query Error:", e)
            return []