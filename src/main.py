# src/main.py
import os
from pdf_loader import convert_pdf_to_html
from html_parser import clean_and_structure_html
from html_to_json import html_to_json
from json_to_jsonld import json_to_jsonld
from jsonld_chunker import chunk_jsonld
from chunk_to_graph import process_chunks
#from query_pipeline import ask_question
def main():
    print("🚀 FULL PIPELINE: PDF → HTML → JSON → JSON-LD\n")

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src_dir = os.path.dirname(__file__)
    output_dir = os.path.join(src_dir, "output")

    os.makedirs(output_dir, exist_ok=True)

    pdf_path = os.path.join(base_dir, "data", "sbc.pdf")

    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return

    raw_html_path = os.path.join(output_dir, "docling_raw.html")
    structured_html_path = os.path.join(output_dir, "structured_html.html")
    json_path = os.path.join(output_dir, "structured_data.json")
    jsonld_path = os.path.join(output_dir, "graph_data.json")

    # STEP 1
    print("📄 Converting PDF → HTML...")
    raw_html = convert_pdf_to_html(pdf_path, raw_html_path)

    # STEP 2
    print("🧹 Structuring HTML...")
    structured_html = clean_and_structure_html(raw_html, structured_html_path)

    # STEP 3
    print("🔄 Converting HTML → JSON...")
    html_to_json(structured_html_path, json_path)  
    # STEP 4
    print("🔗 Converting JSON → JSON-LD...")
    json_to_jsonld(json_path, jsonld_path)        


    # STEP 5: JSON-LD → CHUNKS
    print("🧩 Creating structural chunks...")
    chunk_path = os.path.join(output_dir, "chunks.json")

    chunk_jsonld(jsonld_path, chunk_path)
    # STEP 6: LLM + Neo4j
    print("🧠 Extracting graph via LLM and saving outputs...")

    process_chunks(chunk_path, output_dir)

    print("\n🎉 Pipeline completed successfully!")
    print(f"📁 Check output folder: {output_dir}")


if __name__ == "__main__":
    main()