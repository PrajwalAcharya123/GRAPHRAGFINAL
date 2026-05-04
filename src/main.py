# # import os
# # from pdf_loader import convert_pdf_to_html
# # from html_parser import clean_and_structure_html
# # from structuralhtml_chunker import chunk_html
# # from graph_processor import process_chunks


# # def main():
# #     print("🚀 FULL PIPELINE STARTED\n")

# #     base_dir = os.path.dirname(os.path.abspath(__file__))
# #     output_dir = os.path.join(base_dir, "output")
# #     os.makedirs(output_dir, exist_ok=True)

# #     pdf_path = os.path.join(base_dir, "..", "data", "sbc.pdf")

# #     raw_html_path = os.path.join(output_dir, "docling_raw.html")
# #     structured_html_path = os.path.join(output_dir, "structured_html.html")
# #     chunk_path = os.path.join(output_dir, "chunksforllm.json")

# #     # STEP 1
# #     print("📄 PDF → HTML")
# #     raw_html = convert_pdf_to_html(pdf_path, raw_html_path)

# #     # STEP 2
# #     print("🧹 Cleaning HTML")
# #     clean_and_structure_html(raw_html, structured_html_path)

# #     # STEP 3
# #     print("🧩 Chunking")
# #     chunk_html(structured_html_path, chunk_path)

# #     # STEP 4 (FINAL)
# #     print("🧠 Extracting Graph + Storing in Neo4j")
# #     process_chunks(chunk_path, output_dir)

# #     print("\n🎉 PIPELINE COMPLETED")


# # if __name__ == "__main__":
# #     main()


# import os
# from pdf_to_images import convert_pdf_to_images
# from vision_extractor import extract_page
# from utils import save_json
# from postprocess import merge_pages
# from merge_html import merge_html_pages   # ✅ NEW IMPORT
# from structuralhtml_chunker import chunk_html
# from graph_processor import process_chunks



import os
from pdf_to_images import convert_pdf_to_images
from vision_extractor import extract_page
#from utils import save_json
#from postprocess import merge_pages
from merge_html import merge_html_pages
from structuralhtml_chunker import chunk_html
from graph_processor import process_chunks

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PDF_PATH = os.path.join(BASE_DIR, "data", "sbc.pdf")
IMAGE_DIR = os.path.join(BASE_DIR, "output", "pages")
#RAW_DIR = os.path.join(BASE_DIR, "output", "raw_llm")
#FINAL_JSON = os.path.join(BASE_DIR, "output", "final_json", "sbc.json")
HTML_DIR = os.path.join(BASE_DIR, "output", "html")
COMBINED_HTML = os.path.join(BASE_DIR, "output", "combined.html")

#  FIXED PATHS
output_dir = os.path.join(BASE_DIR, "output")
chunk_path = os.path.join(output_dir, "chunksforllm2.json")


def main():
    print(" Converting PDF to images...")
   # images = convert_pdf_to_images(PDF_PATH, IMAGE_DIR)

    print(" Extracting with Vision LLM...")
    os.makedirs(HTML_DIR, exist_ok=True)

#    # for i, img in enumerate(images):
#         print(f"Processing page {i+1}...")
#         result = extract_page(img, i + 1)

#         html_path = os.path.join(HTML_DIR, f"page_{i+1}.html")
#         with open(html_path, "w", encoding="utf-8") as f:
#             f.write(result)

    print(" Merging JSON output...")
   # merge_pages(RAW_DIR, FINAL_JSON)

    #  STEP 1: Merge HTML
    print(" Merging HTML pages...")
   # merge_html_pages(HTML_DIR, COMBINED_HTML)

    #  STEP 2: Chunk combined HTML
    print("Chunking HTML...")
    # chunk_html(COMBINED_HTML, chunk_path)

    #  STEP 3: Process graph
    print(" Extracting Graph + Storing in Neo4j...")
    process_chunks(chunk_path, output_dir)

    print("\n PIPELINE COMPLETED")


if __name__ == "__main__":
    main()