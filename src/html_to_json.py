# # src/html_to_json.py

# import json
# import os
# from bs4 import BeautifulSoup


# def html_to_json(html_path, output_path):
#     # ✅ Ensure file ends with .json
#     if not output_path.endswith(".json"):
#         output_path += ".json"

#     with open(html_path, "r", encoding="utf-8") as f:
#         soup = BeautifulSoup(f, "html.parser")

#     data = {
#         "document_info": {},
#         "sections": [],
#         "tables": [],
#         "entities": []
#     }

#     # 🔹 Extract paragraphs
#     for p in soup.find_all("p"):
#         text = p.get_text(strip=True)
#         if text:
#             data["sections"].append(text)

#             if "coverage period" in text.lower():
#                 data["document_info"]["coverage_period"] = text
#             if "plan type" in text.lower():
#                 data["document_info"]["plan_type"] = text

#     # 🔹 Process tables
#     for table in soup.find_all("table"):
#         rows = []
#         for row in table.find_all("tr"):
#             cols = [c.get_text(strip=True) for c in row.find_all(["td", "th"])]
#             if cols:
#                 rows.append(cols)

#         if not rows:
#             continue

#         headers = [h.lower().strip() for h in rows[0]]

#         for r in rows[1:]:
#             if len(r) != len(headers):
#                 continue

#             row_data = dict(zip(headers, r))

#             data["entities"].append({
#                 "type": "table_row",
#                 "attributes": row_data
#             })

#     # 💾 Ensure folder exists
#     os.makedirs(os.path.dirname(output_path), exist_ok=True)

#     # 💾 Save JSON properly
#     with open(output_path, "w", encoding="utf-8") as f:
#         json.dump(data, f, indent=2, ensure_ascii=False)

#     print(f"✅ JSON file saved at: {output_path}")

#     return data


# src/html_to_json.py

import json
import os
import re
from bs4 import BeautifulSoup


def clean_money(value):
    """Extract numeric value from $ text"""
    if not value:
        return None
    match = re.findall(r"\d+", value.replace(",", ""))
    return int(match[0]) if match else None


def html_to_json(html_path, output_path):
    if not output_path.endswith(".json"):
        output_path += ".json"

    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    data = {
        "entities": [],
        "relationships": []
    }

    # =========================
    # 🔹 PLAN NODE
    # =========================
    plan_id = "plan_1"

    data["entities"].append({
        "id": plan_id,
        "type": "HealthPlan",
        "name": "SBC Plan"
    })

    # =========================
    # 🔹 EXTRACT PARAGRAPHS
    # =========================
    for p in soup.find_all("p"):
        text = p.get_text(strip=True).lower()

        if "coverage period" in text:
            data["entities"].append({
                "id": "coverage_1",
                "type": "CoveragePeriod",
                "text": text
            })
            data["relationships"].append({
                "from": plan_id,
                "to": "coverage_1",
                "type": "HAS_COVERAGE_PERIOD"
            })

        if "plan type" in text:
            data["entities"].append({
                "id": "plan_type_1",
                "type": "PlanType",
                "name": "PPO"
            })
            data["relationships"].append({
                "from": plan_id,
                "to": "plan_type_1",
                "type": "HAS_PLAN_TYPE"
            })

    # =========================
    # 🔹 TABLE PROCESSING
    # =========================
    tables = soup.find_all("table")

    entity_count = 0
    cost_count = 0

    for table in tables:
        rows = []
        for row in table.find_all("tr"):
            cols = [c.get_text(strip=True) for c in row.find_all(["td", "th"])]
            if cols:
                rows.append(cols)

        if len(rows) < 2:
            continue

        headers = [h.lower() for h in rows[0]]

        # =========================
        # 🔹 IMPORTANT QUESTIONS TABLE
        # =========================
        if "important questions" in headers[0]:
            for r in rows[1:]:
                question = r[0].lower()
                answer = r[1]

                # Deductible
                if "deductible" in question:
                    entity_id = f"deductible_{entity_count}"
                    entity_count += 1

                    data["entities"].append({
                        "id": entity_id,
                        "type": "Deductible",
                        "value_text": answer
                    })

                    data["relationships"].append({
                        "from": plan_id,
                        "to": entity_id,
                        "type": "HAS_DEDUCTIBLE"
                    })

                # Out of pocket
                elif "out-of-pocket" in question:
                    entity_id = f"oop_{entity_count}"
                    entity_count += 1

                    data["entities"].append({
                        "id": entity_id,
                        "type": "OutOfPocketLimit",
                        "value_text": answer
                    })

                    data["relationships"].append({
                        "from": plan_id,
                        "to": entity_id,
                        "type": "HAS_OUT_OF_POCKET_LIMIT"
                    })

                # Referral
                elif "referral" in question:
                    entity_id = f"referral_{entity_count}"
                    entity_count += 1

                    data["entities"].append({
                        "id": entity_id,
                        "type": "ReferralRequirement",
                        "value": answer
                    })

                    data["relationships"].append({
                        "from": plan_id,
                        "to": entity_id,
                        "type": "REQUIRES_REFERRAL"
                    })

        # =========================
        # 🔹 SERVICE TABLES
        # =========================
        elif "services you may need" in headers:
            for r in rows[1:]:

                if len(r) < 3:
                    continue

                service_name = r[1]
                network_cost = r[2]
                out_cost = r[3] if len(r) > 3 else ""

                service_id = f"service_{entity_count}"
                entity_count += 1

                data["entities"].append({
                    "id": service_id,
                    "type": "MedicalService",
                    "name": service_name
                })

                data["relationships"].append({
                    "from": plan_id,
                    "to": service_id,
                    "type": "COVERS"
                })

                # Cost node
                cost_id = f"cost_{cost_count}"
                cost_count += 1

                data["entities"].append({
                    "id": cost_id,
                    "type": "Cost",
                    "network_cost": network_cost,
                    "out_of_network_cost": out_cost
                })

                data["relationships"].append({
                    "from": service_id,
                    "to": cost_id,
                    "type": "HAS_COST"
                })

    # =========================
    # 🔹 EXCLUDED SERVICES
    # =========================
    for h in soup.find_all("h2"):
        if "excluded services" in h.get_text().lower():
            ul = h.find_next("table")
            if ul:
                text = ul.get_text()
                services = re.split(r"•", text)

                for s in services:
                    s = s.strip()
                    if not s:
                        continue

                    sid = f"excluded_{entity_count}"
                    entity_count += 1

                    data["entities"].append({
                        "id": sid,
                        "type": "ExcludedService",
                        "name": s
                    })

                    data["relationships"].append({
                        "from": plan_id,
                        "to": sid,
                        "type": "EXCLUDES"
                    })

    # =========================
    # 💾 SAVE
    # =========================
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ JSON saved: {output_path}")
    return data