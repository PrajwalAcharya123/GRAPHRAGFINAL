# # src/structuralhtml_chunker.py

# import os
# import json
# import re
# from bs4 import BeautifulSoup


# # ✅ Self-contained clean_text (no external dependency)
# def clean_text(text):
#     if not text:
#         return ""
#     return re.sub(r"\s+", " ", text).strip()


# # ✅ TABLE EXTRACTION (robust)
# def extract_tables(soup):
#     chunks = []
#     tables = soup.find_all("table")

#     for t_idx, table in enumerate(tables):

#         rows = table.find_all("tr")
#         if not rows:
#             continue

#         header_grid = []

#         # 🔹 Detect headers (th OR bold td)
#         for row in rows:
#             ths = row.find_all("th")

#             # fallback: detect header inside td (common in PDF HTML)
#             if not ths:
#                 tds = row.find_all("td")
#                 if all(td.find("b") or td.find("strong") for td in tds):
#                     ths = tds
#                 else:
#                     break

#             current_row = []

#             for cell in ths:
#                 text = clean_text(cell.get_text())
#                 colspan = int(cell.get("colspan", 1))
#                 rowspan = int(cell.get("rowspan", 1))

#                 current_row.append({
#                     "text": text,
#                     "colspan": colspan,
#                     "rowspan": rowspan
#                 })

#             header_grid.append(current_row)

#         # 🔹 Expand header grid (handle rowspan/colspan)
#         def expand_headers(header_grid):
#             grid = []

#             for r_idx, row in enumerate(header_grid):
#                 col_idx = 0

#                 while len(grid) <= r_idx:
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

#         # 🔹 Safety check (fix crash)
#         if not expanded or not expanded[-1]:
#             continue

#         # 🔹 Create final headers
#         final_headers = []
#         num_cols = len(expanded[-1])

#         for col in range(num_cols):
#             parts = []
#             for row in expanded:
#                 if col < len(row) and row[col]:
#                     parts.append(row[col])
#             final_headers.append(" | ".join(parts))

#         # 🔹 Extract data rows
#         data_rows = rows[len(header_grid):]

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


# # ✅ SECTION EXTRACTION (headings + paragraphs)
# def extract_sections(soup):
#     chunks = []

#     current_section = None
#     content_buffer = []

#     for tag in soup.find_all(["h1", "h2", "h3", "p"]):

#         if tag.name in ["h1", "h2", "h3"]:

#             if current_section and content_buffer:
#                 chunks.append({
#                     "chunk_id": f"section_{len(chunks)}",
#                     "type": "section",
#                     "title": current_section,
#                     "content": " ".join(content_buffer)
#                 })
#                 content_buffer = []

#             current_section = clean_text(tag.get_text())

#         elif tag.name == "p":
#             text = clean_text(tag.get_text())
#             if text:
#                 content_buffer.append(text)

#     if current_section and content_buffer:
#         chunks.append({
#             "chunk_id": f"section_{len(chunks)}",
#             "type": "section",
#             "title": current_section,
#             "content": " ".join(content_buffer)
#         })

#     return chunks


# # ✅ LIST EXTRACTION
# def extract_lists(soup):
#     chunks = []

#     lists = soup.find_all("ul")

#     for l_idx, ul in enumerate(lists):
#         items = [clean_text(li.get_text()) for li in ul.find_all("li")]

#         chunks.append({
#             "chunk_id": f"list_{l_idx}",
#             "type": "list",
#             "items": items
#         })

#     return chunks


# # ✅ MAIN CHUNK FUNCTION
# def chunk_html(input_html_path, output_path):
#     with open(input_html_path, "r", encoding="utf-8") as f:
#         soup = BeautifulSoup(f, "html.parser")

#     chunks = []

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

#     # 🔹 Save JSON
#     os.makedirs(os.path.dirname(output_path), exist_ok=True)

#     with open(output_path, "w", encoding="utf-8") as f:
#         json.dump(chunks, f, indent=2, ensure_ascii=False)

#     print(f"✅ HTML chunks saved at: {output_path}")
#     print(f"📦 Total chunks: {len(chunks)}")

#     return chunks

# # import os
# # import json
# # from bs4 import BeautifulSoup
# # from html_to_json import clean_text

# # # =========================
# # # TABLE EXTRACTION (FIXED)
# # # =========================
# # def extract_tables(soup):
# #     chunks = []
# #     tables = soup.find_all("table")

# #     for t_idx, table in enumerate(tables):
# #         rows = table.find_all("tr")

# #         if not rows:
# #             continue

# #         # STEP 1: Extract header rows
# #         header_grid = []

# #         for row in rows:
# #             ths = row.find_all("th")
# #             if not ths:
# #                 break

# #             current_row = []
# #             for th in ths:
# #                 current_row.append({
# #                     "text": clean_text(th.get_text()),
# #                     "colspan": int(th.get("colspan", 1)),
# #                     "rowspan": int(th.get("rowspan", 1))
# #                 })

# #             header_grid.append(current_row)

# #         # =========================
# #         # STEP 2: Expand headers
# #         # =========================
# #         def expand_headers(header_grid):
# #             grid = []

# #             for r_idx, row in enumerate(header_grid):
# #                 col_idx = 0

# #                 if len(grid) <= r_idx:
# #                     grid.append([])

# #                 for cell in row:
# #                     while col_idx < len(grid[r_idx]) and grid[r_idx][col_idx] is not None:
# #                         col_idx += 1

# #                     for i in range(cell["colspan"]):
# #                         for j in range(cell["rowspan"]):
# #                             while len(grid) <= r_idx + j:
# #                                 grid.append([])

# #                             while len(grid[r_idx + j]) <= col_idx + i:
# #                                 grid[r_idx + j].append(None)

# #                             grid[r_idx + j][col_idx + i] = cell["text"]

# #                     col_idx += cell["colspan"]

# #             return grid

# #         expanded = expand_headers(header_grid)

# #         # =========================
# #         # STEP 3: Create headers safely
# #         # =========================
# #         if not expanded or not expanded[-1]:
# #             # fallback: infer columns
# #             first_row = None
# #             for r in rows:
# #                 tds = r.find_all("td")
# #                 if tds:
# #                     first_row = tds
# #                     break

# #             if not first_row:
# #                 print(f"⚠️ Skipping empty table {t_idx}")
# #                 continue

# #             final_headers = [f"col_{i}" for i in range(len(first_row))]
# #             data_start_idx = 0

# #         else:
# #             final_headers = []
# #             num_cols = len(expanded[-1])

# #             for col in range(num_cols):
# #                 parts = []
# #                 for row in expanded:
# #                     if col < len(row) and row[col]:
# #                         parts.append(row[col])

# #                 # remove duplicates like "A | A | A"
# #                 unique_parts = list(dict.fromkeys(parts))
# #                 final_headers.append(" | ".join(unique_parts) if unique_parts else f"col_{col}")

# #             data_start_idx = len(header_grid)

# #         # =========================
# #         # STEP 4: Merge broken rows (CRITICAL)
# #         # =========================
# #         data_rows = rows[data_start_idx:]

# #         merged_rows = []
# #         buffer = None

# #         for row in data_rows:
# #             cols = [clean_text(td.get_text()) for td in row.find_all("td")]

# #             if not cols:
# #                 continue

# #             # new row starts
# #             if cols[0]:
# #                 if buffer:
# #                     merged_rows.append(buffer)
# #                 buffer = cols
# #             else:
# #                 # continuation row
# #                 if buffer:
# #                     for i in range(len(cols)):
# #                         if i < len(buffer):
# #                             buffer[i] += " " + cols[i]

# #         if buffer:
# #             merged_rows.append(buffer)

# #         # =========================
# #         # STEP 5: Convert to chunks
# #         # =========================
# #         for r_idx, cols in enumerate(merged_rows):
# #             row_data = {}

# #             for i, col in enumerate(cols):
# #                 key = final_headers[i] if i < len(final_headers) else f"col_{i}"
# #                 row_data[key] = col

# #             chunks.append({
# #                 "chunk_id": f"table_{t_idx}_row_{r_idx}",
# #                 "type": "table_row",
# #                 "data": row_data
# #             })

# #             return chunks
# #         # STEP 2: Expand headers (safe)
# #         def expand_headers(header_grid):
# #             grid = []

# #             for r_idx, row in enumerate(header_grid):
# #                 col_idx = 0

# #                 if len(grid) <= r_idx:
# #                     grid.append([])

# #                 for cell in row:
# #                     while col_idx < len(grid[r_idx]) and grid[r_idx][col_idx] is not None:
# #                         col_idx += 1

# #                     for i in range(cell["colspan"]):
# #                         for j in range(cell["rowspan"]):
# #                             while len(grid) <= r_idx + j:
# #                                 grid.append([])

# #                             while len(grid[r_idx + j]) <= col_idx + i:
# #                                 grid[r_idx + j].append(None)

# #                             grid[r_idx + j][col_idx + i] = cell["text"]

# #                     col_idx += cell["colspan"]

# #             return grid

# #         expanded = expand_headers(header_grid)

# #         # =========================
# #         # SAFE HEADER HANDLING
# #         # =========================
# #         if not expanded or len(expanded) == 0 or not expanded[-1]:
# #             # fallback: use first valid row
# #             first_row = None
# #             for r in rows:
# #                 tds = r.find_all("td")
# #                 if tds:
# #                     first_row = tds
# #                     break

# #             if not first_row:
# #                 print(f"⚠️ Skipping empty table {t_idx}")
# #                 continue

# #             final_headers = [f"col_{i}" for i in range(len(first_row))]
# #             data_start_idx = 0

# #         else:
# #             final_headers = []
# #             num_cols = len(expanded[-1])

# #             for col in range(num_cols):
# #                 parts = []
# #                 for row in expanded:
# #                     if col < len(row) and row[col]:
# #                         parts.append(row[col])

# #                 final_headers.append(" | ".join(parts) if parts else f"col_{col}")

# #             data_start_idx = len(header_grid)

# #         # =========================
# #         # EXTRACT DATA ROWS
# #         # =========================
# #         data_rows = rows[data_start_idx:]

# #         for r_idx, row in enumerate(data_rows):
# #             cols = row.find_all("td")

# #             if not cols:
# #                 continue

# #             row_data = {}

# #             for i, td in enumerate(cols):
# #                 key = final_headers[i] if i < len(final_headers) else f"col_{i}"
# #                 row_data[key] = clean_text(td.get_text())

# #             chunks.append({
# #                 "chunk_id": f"table_{t_idx}_row_{r_idx}",
# #                 "type": "table_row",
# #                 "data": row_data
# #             })

# #     return chunks


# # # =========================
# # # SECTION EXTRACTION
# # # =========================
# # def extract_sections(soup):
# #     chunks = []
# #     current_section = None
# #     buffer = []

# #     for tag in soup.find_all(["h1", "h2", "h3", "p"]):
# #         if tag.name in ["h1", "h2", "h3"]:
# #             if current_section and buffer:
# #                 chunks.append({
# #                     "chunk_id": f"section_{len(chunks)}",
# #                     "type": "section",
# #                     "title": current_section,
# #                     "content": " ".join(buffer)
# #                 })
# #                 buffer = []

# #             current_section = clean_text(tag.get_text())

# #         elif tag.name == "p":
# #             text = clean_text(tag.get_text())
# #             if text:
# #                 buffer.append(text)

# #     if current_section and buffer:
# #         chunks.append({
# #             "chunk_id": f"section_{len(chunks)}",
# #             "type": "section",
# #             "title": current_section,
# #             "content": " ".join(buffer)
# #         })

# #     return chunks


# # # =========================
# # # LIST EXTRACTION
# # # =========================
# # def extract_lists(soup):
# #     chunks = []

# #     for i, ul in enumerate(soup.find_all("ul")):
# #         items = [clean_text(li.get_text()) for li in ul.find_all("li")]

# #         chunks.append({
# #             "chunk_id": f"list_{i}",
# #             "type": "list",
# #             "items": items
# #         })

# #     return chunks


# # # =========================
# # # MAIN CHUNK FUNCTION
# # # =========================
# # def chunk_html(input_html_path, output_path):
# #     with open(input_html_path, "r", encoding="utf-8") as f:
# #         soup = BeautifulSoup(f, "html.parser")

# #     chunks = []

# #     # Safe execution
# #     try:
# #         chunks.extend(extract_tables(soup))
# #     except Exception as e:
# #         print(f"❌ Table extraction failed: {e}")

# #     try:
# #         chunks.extend(extract_sections(soup))
# #     except Exception as e:
# #         print(f"❌ Section extraction failed: {e}")

# #     try:
# #         chunks.extend(extract_lists(soup))
# #     except Exception as e:
# #         print(f"❌ List extraction failed: {e}")

# #     # Ensure output folder exists
# #     output_dir = os.path.dirname(output_path)
# #     if output_dir:
# #         os.makedirs(output_dir, exist_ok=True)

# #     # Save JSON
# #     with open(output_path, "w", encoding="utf-8") as f:
# #         json.dump(chunks, f, indent=2, ensure_ascii=False)

# #     print(f"✅ HTML chunks saved at: {output_path}")
# #     print(f"📦 Total chunks: {len(chunks)}")

# #     return chunks




import os, json, re
from bs4 import BeautifulSoup, Tag


# ══════════════════════════════════════════════════════════════════
# UTILITIES
# ══════════════════════════════════════════════════════════════════

def clean(text):
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()

def node_text(tag):
    return clean(tag.get_text())

BENEFIT_TABLE_SIGNAL = {"common medical event", "services you may need"}
IMPORTANT_Q_SIGNAL   = {"important questions", "answers"}
COST_SHARE_SIGNAL    = {"cost sharing"}
PLAN_PARAMS_SIGNAL   = {"specialist copayment", "the plan's overall deductible",
                        "hospital (facility) coinsurance"}
TOTAL_COST_SIGNAL    = {"total example cost"}


def classify_table(table):
    """Return one of: 'benefit', 'important_q', 'cost_share',
       'plan_params', 'total_cost', 'junk'."""
    rows = table.find_all("tr")
    if not rows:
        return "junk"
    header_text = {clean(c.get_text()).lower()
                   for r in rows[:3] for c in r.find_all(["th", "td"])}
    if BENEFIT_TABLE_SIGNAL <= header_text:
        return "benefit"
    if IMPORTANT_Q_SIGNAL <= header_text:
        return "important_q"
    if COST_SHARE_SIGNAL & header_text:
        return "cost_share"
    if PLAN_PARAMS_SIGNAL & header_text:
        return "plan_params"
    if TOTAL_COST_SIGNAL & header_text:
        return "total_cost"
    return "junk"


# ══════════════════════════════════════════════════════════════════
# GRID ENGINE  (rowspan / colspan → flat dict)
# ══════════════════════════════════════════════════════════════════

def build_grid(rows):
    grid, is_header, rowspan_src = {}, {}, {}
    for r_idx, row in enumerate(rows):
        col = 0
        for cell in row.find_all(["th", "td"]):
            while (r_idx, col) in grid:
                col += 1
            text    = clean(cell.get_text())
            cs      = int(cell.get("colspan", 1))
            rs      = int(cell.get("rowspan", 1))
            hdr     = cell.name == "th" or bool(cell.find(["b", "strong"]))
            for dr in range(rs):
                for dc in range(cs):
                    pos = (r_idx + dr, col + dc)
                    grid[pos]        = text
                    is_header[pos]   = hdr
                    rowspan_src[pos] = r_idx
            col += cs
    num_cols = max((c for _, c in grid), default=-1) + 1
    return grid, is_header, rowspan_src, num_cols


def header_row_count(grid, is_header, num_rows, num_cols):
    count = 0
    for r in range(num_rows):
        positions = [(r, c) for c in range(num_cols) if (r, c) in grid]
        if not positions:
            continue
        ratio = sum(1 for p in positions if is_header.get(p)) / len(positions)
        if ratio >= 0.5:
            count += 1
        else:
            break
    return count


def column_labels(grid, hrc, num_cols):
    labels = []
    for c in range(num_cols):
        parts, seen = [], set()
        for r in range(hrc):
            v = grid.get((r, c), "")
            if v and v not in seen:
                parts.append(v); seen.add(v)
        labels.append(" | ".join(parts) or f"col_{c}")
    return labels


def parent_col_index(grid, rowspan_src, hrc, num_rows, num_cols):
    """Column with the fewest 'original' (non-inherited) data rows = spanner."""
    if num_cols <= 1:
        return None
    orig = [
        sum(1 for r in range(hrc, num_rows)
            if (r, c) in rowspan_src and rowspan_src[(r, c)] == r)
        for c in range(num_cols)
    ]
    m = min(orig)
    return orig.index(m) if m < (num_rows - hrc) else 0


# ══════════════════════════════════════════════════════════════════
# CROSS-PAGE TABLE STITCHER
# ══════════════════════════════════════════════════════════════════

def stitch_benefit_tables(tables):
    """
    Docling splits the benefits table across page breaks.  Each fragment
    re-emits the full <thead>, so we detect them by schema and merge their
    <tbody> rows into one virtual table (a list of <tr> tags).

    Special case: the first data row of a continuation table sometimes
    contains only a partial limitation string (the "benefits by 50%…" 
    orphan).  We detect this and append it to the last chunk of the
    previous fragment instead of creating a new service row.
    """
    benefit_tables = [t for t in tables if classify_table(t) == "benefit"]
    if not benefit_tables:
        return []

    # Merge all rows; track which rows are "orphan limitation fragments"
    merged_rows = []
    orphan_limitations = []   # (insertion_index, text)

    for t_idx, table in enumerate(benefit_tables):
        rows = table.find_all("tr")
        grid, is_header, rowspan_src, num_cols = build_grid(rows)
        hrc  = header_row_count(grid, is_header, len(rows), num_cols)

        for r in range(hrc, len(rows)):
            cells = rows[r].find_all(["th", "td"])
            # Detect orphan: row has cells but col-0 is empty / inherited
            # AND the row only has limitation text (1-2 non-empty cells)
            non_empty = [clean(c.get_text()) for c in cells if clean(c.get_text())]
            if (t_idx > 0 and len(non_empty) <= 2
                    and not any(
                        kw in non_empty[0].lower()
                        for kw in ["if ", "physician", "services", "care", "drugs"]
                    ) if non_empty else False):
                orphan_limitations.append((len(merged_rows), non_empty[0] if non_empty else ""))
            else:
                merged_rows.append(rows[r])

    return merged_rows, orphan_limitations


# ══════════════════════════════════════════════════════════════════
# BENEFIT TABLE CHUNKER
# ══════════════════════════════════════════════════════════════════

NONE_PATTERN = re.compile(r"^-+None-+$")
PREAUTH_PATTERN = re.compile(r"preauthorization", re.I)

def extract_benefit_chunks(tables):
    result = stitch_benefit_tables(tables)
    if not result:
        return []
    merged_rows, orphan_limitations = result

    # Build grid from merged rows directly
    grid, is_header, rowspan_src, num_cols = build_grid(merged_rows)
    num_rows = len(merged_rows)
    hrc      = header_row_count(grid, is_header, num_rows, num_cols)

    # The merged rows already start at data rows (headers were consumed
    # during stitching), so hrc should be 0 here — but guard anyway.
    col_lbls = column_labels(grid, hrc, num_cols)
    pcol     = parent_col_index(grid, rowspan_src, hrc, num_rows, num_cols)

    # Canonical column names (positional fallback)
    # Col 0 = Medical Event, 1 = Service, 2 = Network, 3 = OON, 4 = Limits
    
    COL_EVENT   = col_lbls[0] if num_cols > 0 else "col_0"
    COL_SERVICE = col_lbls[1] if num_cols > 1 else "col_1"
    COL_NET     = col_lbls[2] if num_cols > 2 else "col_2"
    COL_OON     = col_lbls[3] if num_cols > 3 else "col_3"
    COL_LIMITS  = col_lbls[4] if num_cols > 4 else "col_4"

    chunks = []
    entity_label  = ""
    entity_id     = None
    entity_seq    = 0

    for r in range(hrc, num_rows):
        row_data = {col_lbls[c]: grid.get((r, c), "") for c in range(num_cols)}
        if not any(row_data.values()):
            continue

        # ── parent entity tracking ────────────────────────────────
        if pcol is not None:
            pk      = col_lbls[pcol]
            src_row = rowspan_src.get((r, pcol), r)
            if src_row == r:
                new_label = row_data.get(pk, "").strip()
                if new_label:
                    entity_label = new_label
                    entity_id    = f"event_{entity_seq:03d}"
                    entity_seq  += 1
            row_data[pk] = entity_label

        service  = row_data.get(COL_SERVICE, "")
        net_cost = row_data.get(COL_NET, "")
        oon_cost = row_data.get(COL_OON, "")
        limits   = row_data.get(COL_LIMITS, "")

        # Normalise "None" sentinel
        if NONE_PATTERN.match(limits.strip()):
            limits = ""

        chunks.append({
            "chunk_id"        : f"benefit_{len(chunks):03d}",
            "type"            : "benefit_service",
            # ── relationship ──────────────────────────────────────
            "medical_event"   : entity_label,
            "medical_event_id": entity_id,
            # ── service identity ──────────────────────────────────
            "service"         : service,
            # ── cost data ─────────────────────────────────────────
            "network_cost"    : net_cost,
            "out_of_network_cost": oon_cost,
            # ── policy detail ─────────────────────────────────────
            "limitations"     : limits,
            "requires_preauth": bool(PREAUTH_PATTERN.search(limits)),
            # ── full row for completeness ─────────────────────────
            "raw": row_data,
        })

    # Apply orphan limitations (page-break fragments) to prior chunks
    for insert_idx, orphan_text in orphan_limitations:
        target_idx = insert_idx - 1
        if 0 <= target_idx < len(chunks):
            existing = chunks[target_idx]["limitations"]
            chunks[target_idx]["limitations"] = (
                (existing + " " + orphan_text).strip() if existing else orphan_text
            )

    return chunks


# ══════════════════════════════════════════════════════════════════
# IMPORTANT QUESTIONS CHUNKER
# ══════════════════════════════════════════════════════════════════

def extract_important_questions(table):
    rows  = table.find_all("tr")
    grid, _, _, num_cols = build_grid(rows)
    hrc   = 1  # always one header row
    chunks = []
    for r in range(hrc, len(rows)):
        q      = grid.get((r, 0), "")
        answer = grid.get((r, 1), "")
        why    = grid.get((r, 2), "")
        if not q:
            continue
        chunks.append({
            "chunk_id": f"iq_{r - hrc:03d}",
            "type"    : "important_question",
            "question": q,
            "answer"  : answer,
            "why_it_matters": why,
        })
    return chunks


# ══════════════════════════════════════════════════════════════════
# COVERAGE EXAMPLE ASSEMBLER
# ══════════════════════════════════════════════════════════════════

def assemble_coverage_examples(soup):
    """
    Each example has this DOM pattern:
      <h2>Name …</h2>
      <p>(subtitle)</p>
      <table>  plan params (deductible, copay…)  </table>
      <h2>This EXAMPLE event includes services like:</h2>
      <p>service1</p><p>service2</p>…
      <table>  Total Example Cost | $X  </table>
      <h2>In this example, Name would pay:</h2>
      <table>  Cost Sharing breakdown  </table>

    We walk the top-level elements and group them by example.
    """
    EXAMPLE_NAMES = re.compile(
        r"^(Peg is Having|Mia'?s Simple|Managing Joe)", re.I
    )
    examples = []
    current  = None

    # Walk direct children of <body> (or outermost <p class="page">)
    body = soup.find("body")
    # Docling wraps everything in a stray <p class="page"> — flatten it
    container = body.find("p", class_="page") or body

    def iter_elements(parent):
        for child in parent.children:
            if isinstance(child, Tag):
                yield child

    for el in iter_elements(container):
        if el.name in ("h1", "h2", "h3"):
            heading = clean(el.get_text())
            if EXAMPLE_NAMES.match(heading):
                if current:
                    examples.append(current)
                current = {
                    "name"           : heading,
                    "subtitle"       : "",
                    "plan_parameters": {},
                    "included_services": [],
                    "total_cost"     : "",
                    "cost_breakdown" : {},
                    "patient_total"  : "",
                    "_state"         : "params",   # internal parse state
                }
                continue
            if current:
                if "example event includes" in heading.lower():
                    current["_state"] = "services"
                elif "would pay" in heading.lower():
                    current["_state"] = "breakdown"
                continue

        if current is None:
            continue

        state = current["_state"]

        if el.name == "p":
            txt = clean(el.get_text())
            if not txt:
                continue
            if state == "params" and not current["subtitle"]:
                current["subtitle"] = txt
            elif state == "services":
                current["included_services"].append(txt)

        elif el.name == "table":
            ttype = classify_table(el)

            if ttype == "plan_params" and state == "params":
                rows = el.find_all("tr")
                for row in rows:
                    cells = row.find_all(["th", "td"])
                    if len(cells) >= 2:
                        k = clean(cells[0].get_text())
                        v = clean(cells[1].get_text())
                        if k:
                            current["plan_parameters"][k] = v

            elif ttype == "total_cost":
                rows = el.find_all("tr")
                for row in rows:
                    cells = row.find_all(["th", "td"])
                    if len(cells) >= 2:
                        k = clean(cells[0].get_text())
                        v = clean(cells[1].get_text())
                        if "total example cost" in k.lower():
                            current["total_cost"] = v

            elif ttype == "cost_share" and state == "breakdown":
                rows = el.find_all("tr")
                for row in rows:
                    cells = row.find_all(["th", "td"])
                    if len(cells) == 2:
                        k = clean(cells[0].get_text())
                        v = clean(cells[1].get_text())
                        if not k:
                            continue
                        if "total" in k.lower() and "pay" in k.lower():
                            current["patient_total"] = v
                        else:
                            current["cost_breakdown"][k] = v
                    elif len(cells) == 1:
                        pass  # section header row ("Cost Sharing" / "What isn't covered")

    if current:
        examples.append(current)

    # Clean up internal state key and emit chunks
    chunks = []
    for i, ex in enumerate(examples):
        ex.pop("_state", None)
        chunks.append({
            "chunk_id"         : f"example_{i:03d}",
            "type"             : "coverage_example",
            "name"             : ex["name"],
            "subtitle"         : ex["subtitle"],
            "plan_parameters"  : ex["plan_parameters"],
            "included_services": ex["included_services"],
            "total_cost"       : ex["total_cost"],
            "cost_breakdown"   : ex["cost_breakdown"],
            "patient_total"    : ex["patient_total"],
        })
    return chunks


# ══════════════════════════════════════════════════════════════════
# EXCLUDED / OTHER COVERED SERVICES
# ══════════════════════════════════════════════════════════════════

def extract_service_lists(soup):
    chunks  = []
    current_heading = ""

    for el in soup.find_all(["h2", "ul", "p"]):
        if el.name == "h2":
            current_heading = clean(el.get_text())
        elif el.name == "ul":
            is_excluded = "not cover" in current_heading.lower()
            is_other    = "other covered" in current_heading.lower()
            if not (is_excluded or is_other):
                continue
            for li in el.find_all("li"):
                txt = clean(li.get_text())
                if txt:
                    chunks.append({
                        "chunk_id": f"svc_list_{len(chunks):03d}",
                        "type"    : "excluded_service" if is_excluded else "other_covered_service",
                        "service" : txt,
                        "section" : current_heading,
                    })
    # Also rescue the malformed table overflow (purposes / Hearing Aids / Bariatric)
    for table in soup.find_all("table"):
        if classify_table(table) == "junk":
            rows = table.find_all("tr")
            for row in rows:
                for cell in row.find_all("td"):
                    txt = clean(cell.get_text())
                    if txt and txt.lower() not in ("purposes)", ""):
                        chunks.append({
                            "chunk_id": f"svc_list_{len(chunks):03d}",
                            "type"    : "other_covered_service",
                            "service" : txt,
                            "section" : "Other Covered Services (rescued)",
                        })
    return chunks


# ══════════════════════════════════════════════════════════════════
# SECTION / PREAMBLE / FOOTNOTE CHUNKERS
# ══════════════════════════════════════════════════════════════════

_FOOTNOTE_RE = re.compile(
    r"^(note:|all copayment|this is only a summary|about these coverage|"
    r"your rights|language access|does this plan)",
    re.I,
)

def extract_prose(soup):
    chunks  = []
    section = None
    buf     = []
    orphans = []

    SKIP_HEADINGS = re.compile(
        r"(example event includes|would pay|peg is having|mia'?s simple|"
        r"managing joe|this example|excluded services|services your plan|"
        r"other covered)",
        re.I,
    )

    for tag in soup.find_all(["h1", "h2", "h3", "h4", "p"]):
        if tag.name in ("h1", "h2", "h3", "h4"):
            heading = clean(tag.get_text())
            if SKIP_HEADINGS.search(heading):
                continue
            if section and buf:
                chunks.append({
                    "chunk_id": f"section_{len(chunks):03d}",
                    "type"    : "section",
                    "title"   : section,
                    "content" : " ".join(buf),
                })
            section, buf = heading, []

        elif tag.name == "p":
            txt = clean(tag.get_text())
            if not txt:
                continue
            if _FOOTNOTE_RE.match(txt):
                chunks.append({
                    "chunk_id": f"footnote_{len(chunks):03d}",
                    "type"    : "footnote",
                    "content" : txt,
                })
                continue
            # Skip coverage-example service list paragraphs (already handled)
            if any(kw in txt.lower() for kw in
                   ["specialist office visits", "emergency room care",
                    "diagnostic test", "childbirth", "primary care physician",
                    "prescription drugs", "durable medical", "hospital delivery",
                    "in-network", "routine in-network"]):
                continue
            if section:
                buf.append(txt)
            else:
                orphans.append(txt)

    if section and buf:
        chunks.append({
            "chunk_id": f"section_{len(chunks):03d}",
            "type"    : "section",
            "title"   : section,
            "content" : " ".join(buf),
        })
    if orphans:
        chunks.insert(0, {
            "chunk_id": "preamble",
            "type"    : "preamble",
            "content" : " ".join(orphans),
        })
    return chunks


# ══════════════════════════════════════════════════════════════════
# PLAN METADATA
# ══════════════════════════════════════════════════════════════════

def extract_plan_metadata(soup):
    """Pull coverage type and period from the top of the document."""
    texts = []
    body  = soup.find("body")
    for p in (body or soup).find_all("p"):
        t = clean(p.get_text())
        if t:
            texts.append(t)
        if len(texts) >= 5:
            break

    coverage_for = next((t for t in texts if "family" in t.lower() or "individual" in t.lower()), "")
    plan_type    = next((t for t in texts if "ppo" in t.lower() or "hmo" in t.lower()), "")

    return [{
        "chunk_id"    : "plan_metadata",
        "type"        : "plan_metadata",
        "coverage_for": coverage_for,
        "plan_type"   : plan_type,
        "raw_header_texts": texts[:5],
    }]


# ══════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ══════════════════════════════════════════════════════════════════

def chunk_html(input_html_path, output_path):
    with open(input_html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    all_tables = soup.find_all("table")
    chunks = []

    # 1. Plan metadata
    meta = extract_plan_metadata(soup)
    chunks.extend(meta)
    print(f"  plan_metadata     : {len(meta)}")

    # 2. Important Questions (table 0)
    iq_tables = [t for t in all_tables if classify_table(t) == "important_q"]
    iq_chunks = []
    for t in iq_tables:
        iq_chunks.extend(extract_important_questions(t))
    chunks.extend(iq_chunks)
    print(f"  important_question: {len(iq_chunks)}")

    # 3. Benefit services (tables 1+2 stitched)
    benefit_chunks = extract_benefit_chunks(all_tables)
    chunks.extend(benefit_chunks)
    print(f"  benefit_service   : {len(benefit_chunks)}")

    # 4. Excluded / other covered services
    svc_chunks = extract_service_lists(soup)
    chunks.extend(svc_chunks)
    print(f"  service_lists     : {len(svc_chunks)}")

    # 5. Coverage examples (assembled from heading + multiple tables)
    example_chunks = assemble_coverage_examples(soup)
    chunks.extend(example_chunks)
    print(f"  coverage_example  : {len(example_chunks)}")

    # 6. Prose sections + footnotes
    prose_chunks = extract_prose(soup)
    chunks.extend(prose_chunks)
    print(f"  prose/footnotes   : {len(prose_chunks)}")

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)

    print(f"\n  Total: {len(chunks)} chunks  ->  {output_path}")
    return chunks

