      

from neo4j import GraphDatabase
import os
import re
from dotenv import load_dotenv

load_dotenv()


class Neo4jHandler:
    """
    Upgraded Neo4j handler optimized for GraphRAG-style knowledge graphs.

    Improvements:
    - No Value node explosion
    - Typed relationships for attributes (semantic edges)
    - Safer Cypher handling
    - Cleaner graph schema
    """

    def __init__(self):
        self.driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI"),
            auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
        )
        print(" Connected to Neo4j")

        # logging
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.output_dir = os.path.join(self.base_dir, "output")
        os.makedirs(self.output_dir, exist_ok=True)
        self.log_path = os.path.join(self.output_dir, "neo4j_log.txt")

    def close(self):
        self.driver.close()

    def clean_rel_type(self, text: str) -> str:
        """
        Converts any string into Neo4j-safe relationship type.
        """
        return re.sub(r'[^A-Z0-9_]', '_', text.upper())

    def insert_graph_data(self, graph_data: dict):

        entities = graph_data.get("entities", [])
        relationships = graph_data.get("relationships", [])
        attributes = graph_data.get("attributes", [])

        with self.driver.session() as session:

            # 1. CREATE ENTITIES (NODES)
            for entity in entities:
                if not entity:
                    continue

                session.run(
                    "MERGE (n:Entity {name: $name})",
                    name=entity
                )

            # 2. CREATE RELATIONSHIPS
            for src, rel, dst in relationships:
                if not src or not dst:
                    continue

                rel_type = self.clean_rel_type(rel)

                cypher = f"""
                MERGE (a:Entity {{name: $src}})
                MERGE (b:Entity {{name: $dst}})
                MERGE (a)-[r:{rel_type}]->(b)
                """

                session.run(cypher, src=src, dst=dst)

                self._log(f"{src} -[{rel_type}]-> {dst}")

            # 3. ATTRIBUTES 
            for entity, key, value in attributes:
                if not entity or not key or value is None:
                    continue

                key_clean = self.clean_rel_type(key)

                # Instead of Value nodes → use semantic property edges
                value_str = str(value).strip()

                cypher = f"""
                MERGE (e:Entity {{name: $entity}})
                MERGE (e)-[r:{key_clean}]->(v:Value {{value: $value}})
                """

                session.run(
                    cypher,
                    entity=entity,
                    value=value_str
                )

                self._log(f"{entity} -[{key_clean}]-> {value_str}")

        print(" Graph successfully inserted into Neo4j")

    def _log(self, text: str):
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(text + "\n")

    def run_query(self, query: str):
        with self.driver.session() as session:
            result = session.run(query)
            return [record.data() for record in result]


