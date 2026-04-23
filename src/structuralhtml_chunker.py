# src/structuralhtml_chunker.py

import os
import json
import re
from bs4 import BeautifulSoup


# ✅ Self-contained clean_text (no external dependency)
def clean_text(text):
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


# ✅ TABLE EXTRACTION (robust)
def extract_tables(soup):
    chunks = []
    tables = soup.find_all("table")

    for t_idx, table in enumerate(tables):

        rows = table.find_all("tr")
        if not rows:
            continue

        header_grid = []

        # 🔹 Detect headers (th OR bold td)
        for row in rows:
            ths = row.find_all("th")

            # fallback: detect header inside td (common in PDF HTML)
            if not ths:
                tds = row.find_all("td")
                if all(td.find("b") or td.find("strong") for td in tds):
                    ths = tds
                else:
                    break

            current_row = []

            for cell in ths:
                text = clean_text(cell.get_text())
                colspan = int(cell.get("colspan", 1))
                rowspan = int(cell.get("rowspan", 1))

                current_row.append({
                    "text": text,
                    "colspan": colspan,
                    "rowspan": rowspan
                })

            header_grid.append(current_row)

        # 🔹 Expand header grid (handle rowspan/colspan)
        def expand_headers(header_grid):
            grid = []

            for r_idx, row in enumerate(header_grid):
                col_idx = 0

                while len(grid) <= r_idx:
                    grid.append([])

                for cell in row:

                    while col_idx < len(grid[r_idx]) and grid[r_idx][col_idx] is not None:
                        col_idx += 1

                    for i in range(cell["colspan"]):
                        for j in range(cell["rowspan"]):

                            while len(grid) <= r_idx + j:
                                grid.append([])

                            while len(grid[r_idx + j]) <= col_idx + i:
                                grid[r_idx + j].append(None)

                            grid[r_idx + j][col_idx + i] = cell["text"]

                    col_idx += cell["colspan"]

            return grid

        expanded = expand_headers(header_grid)

        # 🔹 Safety check (fix crash)
        if not expanded or not expanded[-1]:
            continue

        # 🔹 Create final headers
        final_headers = []
        num_cols = len(expanded[-1])

        for col in range(num_cols):
            parts = []
            for row in expanded:
                if col < len(row) and row[col]:
                    parts.append(row[col])
            final_headers.append(" | ".join(parts))

        # 🔹 Extract data rows
        data_rows = rows[len(header_grid):]

        for r_idx, row in enumerate(data_rows):
            cols = row.find_all("td")
            if not cols:
                continue

            row_data = {}

            for i, td in enumerate(cols):
                key = final_headers[i] if i < len(final_headers) else f"col_{i}"
                row_data[key] = clean_text(td.get_text())

            chunks.append({
                "chunk_id": f"table_{t_idx}_row_{r_idx}",
                "type": "table_row",
                "data": row_data
            })

    return chunks


# ✅ SECTION EXTRACTION (headings + paragraphs)
def extract_sections(soup):
    chunks = []

    current_section = None
    content_buffer = []

    for tag in soup.find_all(["h1", "h2", "h3", "p"]):

        if tag.name in ["h1", "h2", "h3"]:

            if current_section and content_buffer:
                chunks.append({
                    "chunk_id": f"section_{len(chunks)}",
                    "type": "section",
                    "title": current_section,
                    "content": " ".join(content_buffer)
                })
                content_buffer = []

            current_section = clean_text(tag.get_text())

        elif tag.name == "p":
            text = clean_text(tag.get_text())
            if text:
                content_buffer.append(text)

    if current_section and content_buffer:
        chunks.append({
            "chunk_id": f"section_{len(chunks)}",
            "type": "section",
            "title": current_section,
            "content": " ".join(content_buffer)
        })

    return chunks


# ✅ LIST EXTRACTION
def extract_lists(soup):
    chunks = []

    lists = soup.find_all("ul")

    for l_idx, ul in enumerate(lists):
        items = [clean_text(li.get_text()) for li in ul.find_all("li")]

        chunks.append({
            "chunk_id": f"list_{l_idx}",
            "type": "list",
            "items": items
        })

    return chunks


# ✅ MAIN CHUNK FUNCTION
def chunk_html(input_html_path, output_path):
    with open(input_html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    chunks = []

    try:
        chunks.extend(extract_tables(soup))
    except Exception as e:
        print(f"❌ Table extraction failed: {e}")

    try:
        chunks.extend(extract_sections(soup))
    except Exception as e:
        print(f"❌ Section extraction failed: {e}")

    try:
        chunks.extend(extract_lists(soup))
    except Exception as e:
        print(f"❌ List extraction failed: {e}")

    # 🔹 Save JSON
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)

    print(f"✅ HTML chunks saved at: {output_path}")
    print(f"📦 Total chunks: {len(chunks)}")

    return chunks

# import os
# import json
# from bs4 import BeautifulSoup
# from html_to_json import clean_text

# # =========================
# # TABLE EXTRACTION (FIXED)
# # =========================
# def extract_tables(soup):
#     chunks = []
#     tables = soup.find_all("table")

#     for t_idx, table in enumerate(tables):
#         rows = table.find_all("tr")

#         if not rows:
#             continue

#         # STEP 1: Extract header rows
#         header_grid = []

#         for row in rows:
#             ths = row.find_all("th")
#             if not ths:
#                 break

#             current_row = []
#             for th in ths:
#                 current_row.append({
#                     "text": clean_text(th.get_text()),
#                     "colspan": int(th.get("colspan", 1)),
#                     "rowspan": int(th.get("rowspan", 1))
#                 })

#             header_grid.append(current_row)

#         # =========================
#         # STEP 2: Expand headers
#         # =========================
#         def expand_headers(header_grid):
#             grid = []

#             for r_idx, row in enumerate(header_grid):
#                 col_idx = 0

#                 if len(grid) <= r_idx:
#                     grid.append([])

#                 for cell in row:
#                     while col_idx < len(grid[r_idx]) and grid[r_idx][col_idx] is not None:
#                         col_idx += 1

#                     for i in range(cell["colspan"]):
#                         for j in range(cell["rowspan"]):
#                             while len(grid) <= r_idx + j:
#                                 grid.append([])

#                             while len(grid[r_idx + j]) <= col_idx + i:
#                                 grid[r_idx + j].append(None)

#                             grid[r_idx + j][col_idx + i] = cell["text"]

#                     col_idx += cell["colspan"]

#             return grid

#         expanded = expand_headers(header_grid)

#         # =========================
#         # STEP 3: Create headers safely
#         # =========================
#         if not expanded or not expanded[-1]:
#             # fallback: infer columns
#             first_row = None
#             for r in rows:
#                 tds = r.find_all("td")
#                 if tds:
#                     first_row = tds
#                     break

#             if not first_row:
#                 print(f"⚠️ Skipping empty table {t_idx}")
#                 continue

#             final_headers = [f"col_{i}" for i in range(len(first_row))]
#             data_start_idx = 0

#         else:
#             final_headers = []
#             num_cols = len(expanded[-1])

#             for col in range(num_cols):
#                 parts = []
#                 for row in expanded:
#                     if col < len(row) and row[col]:
#                         parts.append(row[col])

#                 # remove duplicates like "A | A | A"
#                 unique_parts = list(dict.fromkeys(parts))
#                 final_headers.append(" | ".join(unique_parts) if unique_parts else f"col_{col}")

#             data_start_idx = len(header_grid)

#         # =========================
#         # STEP 4: Merge broken rows (CRITICAL)
#         # =========================
#         data_rows = rows[data_start_idx:]

#         merged_rows = []
#         buffer = None

#         for row in data_rows:
#             cols = [clean_text(td.get_text()) for td in row.find_all("td")]

#             if not cols:
#                 continue

#             # new row starts
#             if cols[0]:
#                 if buffer:
#                     merged_rows.append(buffer)
#                 buffer = cols
#             else:
#                 # continuation row
#                 if buffer:
#                     for i in range(len(cols)):
#                         if i < len(buffer):
#                             buffer[i] += " " + cols[i]

#         if buffer:
#             merged_rows.append(buffer)

#         # =========================
#         # STEP 5: Convert to chunks
#         # =========================
#         for r_idx, cols in enumerate(merged_rows):
#             row_data = {}

#             for i, col in enumerate(cols):
#                 key = final_headers[i] if i < len(final_headers) else f"col_{i}"
#                 row_data[key] = col

#             chunks.append({
#                 "chunk_id": f"table_{t_idx}_row_{r_idx}",
#                 "type": "table_row",
#                 "data": row_data
#             })

#             return chunks
#         # STEP 2: Expand headers (safe)
#         def expand_headers(header_grid):
#             grid = []

#             for r_idx, row in enumerate(header_grid):
#                 col_idx = 0

#                 if len(grid) <= r_idx:
#                     grid.append([])

#                 for cell in row:
#                     while col_idx < len(grid[r_idx]) and grid[r_idx][col_idx] is not None:
#                         col_idx += 1

#                     for i in range(cell["colspan"]):
#                         for j in range(cell["rowspan"]):
#                             while len(grid) <= r_idx + j:
#                                 grid.append([])

#                             while len(grid[r_idx + j]) <= col_idx + i:
#                                 grid[r_idx + j].append(None)

#                             grid[r_idx + j][col_idx + i] = cell["text"]

#                     col_idx += cell["colspan"]

#             return grid

#         expanded = expand_headers(header_grid)

#         # =========================
#         # SAFE HEADER HANDLING
#         # =========================
#         if not expanded or len(expanded) == 0 or not expanded[-1]:
#             # fallback: use first valid row
#             first_row = None
#             for r in rows:
#                 tds = r.find_all("td")
#                 if tds:
#                     first_row = tds
#                     break

#             if not first_row:
#                 print(f"⚠️ Skipping empty table {t_idx}")
#                 continue

#             final_headers = [f"col_{i}" for i in range(len(first_row))]
#             data_start_idx = 0

#         else:
#             final_headers = []
#             num_cols = len(expanded[-1])

#             for col in range(num_cols):
#                 parts = []
#                 for row in expanded:
#                     if col < len(row) and row[col]:
#                         parts.append(row[col])

#                 final_headers.append(" | ".join(parts) if parts else f"col_{col}")

#             data_start_idx = len(header_grid)

#         # =========================
#         # EXTRACT DATA ROWS
#         # =========================
#         data_rows = rows[data_start_idx:]

#         for r_idx, row in enumerate(data_rows):
#             cols = row.find_all("td")

#             if not cols:
#                 continue

#             row_data = {}

#             for i, td in enumerate(cols):
#                 key = final_headers[i] if i < len(final_headers) else f"col_{i}"
#                 row_data[key] = clean_text(td.get_text())

#             chunks.append({
#                 "chunk_id": f"table_{t_idx}_row_{r_idx}",
#                 "type": "table_row",
#                 "data": row_data
#             })

#     return chunks


# # =========================
# # SECTION EXTRACTION
# # =========================
# def extract_sections(soup):
#     chunks = []
#     current_section = None
#     buffer = []

#     for tag in soup.find_all(["h1", "h2", "h3", "p"]):
#         if tag.name in ["h1", "h2", "h3"]:
#             if current_section and buffer:
#                 chunks.append({
#                     "chunk_id": f"section_{len(chunks)}",
#                     "type": "section",
#                     "title": current_section,
#                     "content": " ".join(buffer)
#                 })
#                 buffer = []

#             current_section = clean_text(tag.get_text())

#         elif tag.name == "p":
#             text = clean_text(tag.get_text())
#             if text:
#                 buffer.append(text)

#     if current_section and buffer:
#         chunks.append({
#             "chunk_id": f"section_{len(chunks)}",
#             "type": "section",
#             "title": current_section,
#             "content": " ".join(buffer)
#         })

#     return chunks


# # =========================
# # LIST EXTRACTION
# # =========================
# def extract_lists(soup):
#     chunks = []

#     for i, ul in enumerate(soup.find_all("ul")):
#         items = [clean_text(li.get_text()) for li in ul.find_all("li")]

#         chunks.append({
#             "chunk_id": f"list_{i}",
#             "type": "list",
#             "items": items
#         })

#     return chunks


# # =========================
# # MAIN CHUNK FUNCTION
# # =========================
# def chunk_html(input_html_path, output_path):
#     with open(input_html_path, "r", encoding="utf-8") as f:
#         soup = BeautifulSoup(f, "html.parser")

#     chunks = []

#     # Safe execution
#     try:
#         chunks.extend(extract_tables(soup))
#     except Exception as e:
#         print(f"❌ Table extraction failed: {e}")

#     try:
#         chunks.extend(extract_sections(soup))
#     except Exception as e:
#         print(f"❌ Section extraction failed: {e}")

#     try:
#         chunks.extend(extract_lists(soup))
#     except Exception as e:
#         print(f"❌ List extraction failed: {e}")

#     # Ensure output folder exists
#     output_dir = os.path.dirname(output_path)
#     if output_dir:
#         os.makedirs(output_dir, exist_ok=True)

#     # Save JSON
#     with open(output_path, "w", encoding="utf-8") as f:
#         json.dump(chunks, f, indent=2, ensure_ascii=False)

#     print(f"✅ HTML chunks saved at: {output_path}")
#     print(f"📦 Total chunks: {len(chunks)}")

#     return chunks