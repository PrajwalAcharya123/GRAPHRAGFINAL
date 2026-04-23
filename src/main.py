# # src/main.py
# import os
# from pdf_loader import convert_pdf_to_html
# from html_parser import clean_and_structure_html
# from structuralhtml_chunker import chunk_html
# # from chunk_to_graph import process_chunks
# # from query_pipeline import ask_question
# #from extractor import process_chunks
# from graph_processor import process_chunks

# def main():
#     print("🚀 FULL PIPELINE: PDF → HTML → JSON → JSON-LD\n")

#     base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#     src_dir = os.path.dirname(__file__)
#     output_dir = os.path.join(src_dir, "output")

#     os.makedirs(output_dir, exist_ok=True)

#     pdf_path = os.path.join(base_dir, "data", "sbc.pdf")

#     if not os.path.exists(pdf_path):
#         print(f"❌ File not found: {pdf_path}")
#         return

#     raw_html_path = os.path.join(output_dir, "docling_raw.html")
#     structured_html_path = os.path.join(output_dir, "structured_html.html")
   
#     print("📄 Converting PDF → HTML...")
#     raw_html = convert_pdf_to_html(pdf_path, raw_html_path)

#     print("🧹 Structuring HTML...")
#     structured_html = clean_and_structure_html(raw_html, structured_html_path)

#     print("🧩 Creating structural chunks...")
#     chunk_path = os.path.join(output_dir, "chunksforllm.json")

#     chunk_html(structured_html_path, chunk_path)
#     print(f"✅ Chunks saved to: {chunk_path}")
#     # STEP 6: LLM + Neo4j
#     # print("🧠 Extracting graph via LLM and saving outputs...")
#     # input_file = "src/output/chunksforllm.json"
#     #process_chunks(chunk_path, output_dir)
#     #process_chunks(input_file)
#     # print("\n🎉 Pipeline completed successfully!")
#     # print(f"📁 Check output folder: {output_dir}")
#     from extractor import process_chunks

#     chunk_path = os.path.join(output_dir, "chunksforllm.json")
#     output_path = os.path.join(output_dir, "final_graph.json")

#     process_chunks(chunk_path, output_path, batch_size=15)

# if __name__ == "__main__":
#     main()



import os
from pdf_loader import convert_pdf_to_html
from html_parser import clean_and_structure_html
from structuralhtml_chunker import chunk_html
from graph_processor import process_chunks


def main():
    print("🚀 FULL PIPELINE STARTED\n")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    pdf_path = os.path.join(base_dir, "..", "data", "sbc.pdf")

    raw_html_path = os.path.join(output_dir, "docling_raw.html")
    structured_html_path = os.path.join(output_dir, "structured_html.html")
    chunk_path = os.path.join(output_dir, "chunksforllm.json")

    # STEP 1
    print("📄 PDF → HTML")
    raw_html = convert_pdf_to_html(pdf_path, raw_html_path)

    # STEP 2
    print("🧹 Cleaning HTML")
    clean_and_structure_html(raw_html, structured_html_path)

    # STEP 3
    print("🧩 Chunking")
    chunk_html(structured_html_path, chunk_path)

    # STEP 4 (FINAL)
    print("🧠 Extracting Graph + Storing in Neo4j")
    process_chunks(chunk_path, output_dir, batch_size=15)

    print("\n🎉 PIPELINE COMPLETED")


if __name__ == "__main__":
    main()