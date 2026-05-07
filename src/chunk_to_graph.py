# """
# chunk_to_graph.py
# ─────────────────
# Transforms chunks produced by chunk_html() into the exact format
# that the existing Neo4jHandler.insert_graph_data() expects:

#   {
#     "entities"      : ["name1", "name2", ...],
#     "relationships" : [("src", "rel_type", "dst"), ...],
#     "attributes"    : [("entity", "key", "value"), ...],
#   }

# Rules that match the existing handler:
#   - entities   → MERGE (n:Entity {name: $name})
#   - relationships → typed edge between two Entity nodes
#   - attributes → Value node linked to Entity node via typed edge
# """
# from __future__ import annotations
# from typing import Any

# PLAN_NODE = "HealthPlan"


# def _s(v: Any) -> str:
#     return str(v).strip() if v else ""


# # per-type transformers 

# def _plan_metadata(chunk, E, R, A):
#     E.add(PLAN_NODE)
#     cov = _s(chunk.get("coverage_for"))
#     pt  = _s(chunk.get("plan_type"))
#     if cov:
#         A.append((PLAN_NODE, "coverage_for", cov))
#     if pt:
#         A.append((PLAN_NODE, "plan_type", pt))


# def _important_question(chunk, E, R, A):
#     q = _s(chunk.get("question"))
#     if not q:
#         return

#     node_name = f"ImportantQuestion: {q[:80]}..." if len(q) > 80 else q

#     E.add(node_name)
#     E.add(PLAN_NODE)

#     R.append((PLAN_NODE, "HAS_IMPORTANT_QUESTION", node_name))

#     A.append((node_name, "question", q))
#     A.append((node_name, "answer", _s(chunk.get("answer"))))
#     A.append((node_name, "why_it_matters", _s(chunk.get("why_it_matters"))))
#     A.append((node_name, "chunk_id", chunk.get("chunk_id", "")))


# def _benefit_service(chunk, E, R, A):
#     event   = _s(chunk.get("medical_event"))
#     service = _s(chunk.get("service"))
#     net     = _s(chunk.get("network_cost"))
#     oon     = _s(chunk.get("out_of_network_cost"))
#     limits  = _s(chunk.get("limitations"))
#     preauth = chunk.get("requires_preauth", False)
#     copay = _s(chunk.get("copay"))
#     coinsurance = _s(chunk.get("coinsurance"))

#     if not service:
#         return

#     E.add(PLAN_NODE)

#     if event:
#         E.add(event)
#         R.append((PLAN_NODE, "HAS_MEDICAL_EVENT", event))
#         E.add(service)
#         R.append((event, "INCLUDES_SERVICE", service))
#     else:
#         E.add(service)
#         R.append((PLAN_NODE, "HAS_BENEFIT_SERVICE", service))

#     if net:
#         A.append((service, "network_cost", net))
#     if oon:
#         A.append((service, "out_of_network_cost", oon))
#     if limits:
#         A.append((service, "limitations", limits))
#     if preauth:
#         A.append((service, "requires_preauth", "true"))
#     # if copay:
#     #     A.append((service, "copay", copay))

#     # if coinsurance:
#     #     A.append((service, "coinsurance", coinsurance))
#     if copay:
#         A.append((service, "HAS_COPAY", copay))

#     if coinsurance:
#         A.append((service, "HAS_COINSURANCE", coinsurance))

# def _excluded_service(chunk, E, R, A):
#     svc = _s(chunk.get("service"))
#     if not svc:
#         return
#     E.add(PLAN_NODE)
#     E.add(svc)
#     R.append((PLAN_NODE, "EXCLUDES_SERVICE", svc))          # Clear relationship
#     if chunk.get("section"):
#         A.append((svc, "section", chunk["section"]))


# def _other_covered_service(chunk, E, R, A):
#     svc = _s(chunk.get("service"))
#     if not svc:
#         return
#     E.add(PLAN_NODE)
#     E.add(svc)
#     R.append((PLAN_NODE, "COVERS_ADDITIONAL_SERVICE", svc))   # Different relationship
#     if chunk.get("section"):
#         A.append((svc, "section", chunk["section"]))


# def _coverage_example(chunk, E, R, A):
#     name    = _s(chunk.get("name"))
#     total   = _s(chunk.get("total_cost"))
#     patient = _s(chunk.get("patient_total"))
#     cid     = _s(chunk.get("chunk_id"))
#     if not name:
#         return

#     E.add(PLAN_NODE)
#     E.add(name)
#     R.append((PLAN_NODE, "HAS_COVERAGE_EXAMPLE", name))

#     if total:
#         A.append((name, "total_example_cost", total))
#     if patient:
#         A.append((name, "patient_pays", patient))

#     # Plan parameters (deductible, copay…)
#     for k, v in (chunk.get("plan_parameters") or {}).items():
#         k, v = _s(k), _s(v)
#         if k and v:
#             param = f"{name} | {k}"
#             E.add(param)
#             R.append((name, "HAS_PLAN_PARAM", param))
#             A.append((param, "value", v))

#     # Services included in the example
#     for svc in (chunk.get("included_services") or []):
#         svc = _s(svc)
#         if svc:
#             svc_node = f"{name} | {svc}"
#             E.add(svc_node)
#             R.append((name, "INCLUDES_SERVICE", svc_node))

#     # Cost breakdown items
#     for k, v in (chunk.get("cost_breakdown") or {}).items():
#         k, v = _s(k), _s(v)
#         if k and v:
#             cb = f"{name} | {k}"
#             E.add(cb)
#             R.append((name, "HAS_COST_ITEM", cb))
#             A.append((cb, "amount", v))


# def _section(chunk, E, R, A):
#     title   = _s(chunk.get("title")) or "Untitled Section"
#     content = _s(chunk.get("content"))
#     cid     = _s(chunk.get("chunk_id"))
#     node    = f"Section: {title} [{cid}]"
#     E.add(PLAN_NODE)
#     E.add(node)
#     R.append((PLAN_NODE, "HAS_SECTION", node))
#     if content:
#         A.append((node, "content", content))


# def _preamble(chunk, E, R, A):
#     content = _s(chunk.get("content"))
#     E.add(PLAN_NODE)
#     E.add("Preamble")
#     R.append((PLAN_NODE, "HAS_PREAMBLE", "Preamble"))
#     if content:
#         A.append(("Preamble", "content", content))


# def _footnote(chunk, E, R, A):
#     content = _s(chunk.get("content"))
#     cid     = _s(chunk.get("chunk_id"))
#     node    = f"Footnote [{cid}]"
#     E.add(PLAN_NODE)
#     E.add(node)
#     R.append((PLAN_NODE, "HAS_FOOTNOTE", node))
#     if content:
#         A.append((node, "content", content))


# # ── dispatcher ───────────────────────────────────────────────────

# _DISPATCH = {
#     "plan_metadata"         : _plan_metadata,
#     "important_question"    : _important_question,
#     "benefit_service"       : _benefit_service,
#     "excluded_service"      : _excluded_service,
#     "other_covered_service" : _other_covered_service,
#     "coverage_example"      : _coverage_example,
#     "section"               : _section,
#     "preamble"              : _preamble,
#     "footnote"              : _footnote,
# }


# def chunks_to_graph_data(chunks: list[dict]) -> dict:
#     """
#     Convert chunker output into the dict Neo4jHandler.insert_graph_data() expects:
#       {
#         "entities"      : [str, ...],          # unique node names
#         "relationships" : [(src, rel, dst)...], # typed edges
#         "attributes"    : [(entity, key, val)], # node → value edges
#       }
#     """
#     entities: set  = set()
#     rels:     list = []
#     attrs:    list = []

#     for chunk in chunks:
#         fn = _DISPATCH.get(chunk.get("type", ""))
#         if fn:
#             fn(chunk, entities, rels, attrs)

#     return {
#         "entities"      : sorted(entities),
#         "relationships" : rels,
#         "attributes"    : attrs,
#     }

# Newone
"""
chunk_to_graph.py (UPGRADED GRAPH SEMANTIC VERSION)
─────────────────────────────────────────────────────
Transforms chunks into a SEMANTIC GRAPH structure optimized for GraphRAG.

Output:
{
  "entities": ["Node1", "Node2"],
  "relationships": [("src", "REL_TYPE", "dst")],
  "attributes": [("entity", "key", "value")]
}

UPGRADE PRINCIPLES:
- IMPORTANT facts → nodes + relationships (NOT attributes)
- Attributes only for display/metadata
- Costs, limits, rules → first-class graph objects
"""

from __future__ import annotations
from typing import Any
import re

PLAN_NODE = "HealthPlan"


# ─────────────────────────────
# helpers
# ─────────────────────────────

def _s(v: Any) -> str:
    return str(v).strip() if v else ""


def _add(E, R, src, rel, dst):
    """safe relationship builder"""
    if src and dst:
        E.add(src)
        E.add(dst)
        R.append((src, rel, dst))


# def _add_attr(A, entity, key, value):
#     """safe attribute builder"""
#     if entity and value:
#         A.append((entity, key, value))
def _add_attr(A, entity, key, value):
    if not entity:
        return

    if value is None:
        return

    v = str(value).strip()

    if v == "":
        return

    A.append((entity, key, v))


# ─────────────────────────────
# PLAN METADATA
# ─────────────────────────────

def _plan_metadata(chunk, E, R, A):
    E.add(PLAN_NODE)

    cov = _s(chunk.get("coverage_for"))
    pt  = _s(chunk.get("plan_type"))

    if cov:
        _add(E, R, PLAN_NODE, "COVERS", cov)

    if pt:
        _add_attr(A, PLAN_NODE, "plan_type", pt)


# ─────────────────────────────
# IMPORTANT QUESTION
# ─────────────────────────────

# def _important_question(chunk, E, R, A):
#     q = _s(chunk.get("question"))
#     if not q:
#         return

#     node = f"IQ: {q[:80]}" if len(q) > 80 else q

#     _add(E, R, PLAN_NODE, "HAS_IMPORTANT_QUESTION", node)

#     _add_attr(A, node, "question", q)
#     _add_attr(A, node, "answer", chunk.get("answer"))
#     _add_attr(A, node, "why_it_matters", chunk.get("why_it_matters"))

def _important_question(chunk, E, R, A):
    question = _s(chunk.get("question"))
    answer = _s(chunk.get("answer"))
    why_it_matters = _s(chunk.get("why_it_matters"))
    
    if not question or not answer:
        return

    E.add(PLAN_NODE)
    q_lower = question.lower().strip()

    # ── Smart Semantic Mapping ──
    if "overall deductible" in q_lower:
        entity_name = "Overall Deductible"
        _add(E, R, PLAN_NODE, "HAS_DEDUCTIBLE", entity_name)

    elif "services covered before" in q_lower or "before you meet your deductible" in q_lower:
        entity_name = "Services Before Deductible"
        _add(E, R, PLAN_NODE, "COVERS_BEFORE_DEDUCTIBLE", entity_name)

    elif "other deductibles for specific services" in q_lower:
        entity_name = "Service Specific Deductibles"
        _add(E, R, PLAN_NODE, "HAS_SERVICE_SPECIFIC_DEDUCTIBLE", entity_name)

    elif "out-of-pocket limit" in q_lower and "not included" not in q_lower:
        entity_name = "Out-of-Pocket Limit"
        _add(E, R, PLAN_NODE, "HAS_OUT_OF_POCKET_LIMIT", entity_name)

    elif "not included in the out-of-pocket limit" in q_lower:
        entity_name = "Out-of-Pocket Exclusions"
        _add(E, R, PLAN_NODE, "HAS_OUT_OF_POCKET_EXCLUSIONS", entity_name)

    elif "will you pay less if you use a network provider" in q_lower or "network provider" in q_lower:
        entity_name = "Network Provider Benefit"
        _add(E, R, PLAN_NODE, "HAS_NETWORK_ADVANTAGE", entity_name)

    elif "referral to see a specialist" in q_lower or "need a referral" in q_lower:
        entity_name = "Specialist Referral Requirement"
        _add(E, R, PLAN_NODE, "REQUIRES_REFERRAL", entity_name)

    else:
        # Smart fallback
        words = [w for w in question.split() 
                 if w.lower() not in ['what', 'is', 'are', 'the', 'for', 'this', 'plan', 'do', 'you', '?']]
        entity_name = " ".join(words[:7]).strip().title()
        if len(entity_name) > 60:
            entity_name = entity_name[:60]
        
        rel_type = "HAS_INFO"
        if "deductible" in q_lower:
            rel_type = "HAS_DEDUCTIBLE"
        elif "limit" in q_lower:
            rel_type = "HAS_LIMIT"
        elif "covered" in q_lower:
            rel_type = "COVERS"
        
        _add(E, R, PLAN_NODE, rel_type, entity_name)

    # === Store clean, useful attributes ===
    _add_attr(A, entity_name, "value", answer)
    
    if why_it_matters:
        _add_attr(A, entity_name, "why_it_matters", why_it_matters)

    # Optional: Store a short version of the original question for reference
    short_question = question[:150] + "..." if len(question) > 150 else question
    _add_attr(A, entity_name, "question", short_question)


# BENEFIT SERVICE 

import re

# def parse_cost_string(cost_str: str) -> dict:
#     """Smart parser for cost descriptions"""
#     if not cost_str or cost_str.strip() == "":
#         return {}
    
#     cost_str = cost_str.lower().strip()
#     result = {
#         "raw": cost_str,
#         "copay": None,
#         "coinsurance": None,
#         "deductible_applies": True,
#         "notes": []
#     }
    
#     # Extract copay
#     copay_match = re.search(r'(\$\d+[\s-]?(?:copay|per visit|per test|per day|office visit))', cost_str)
#     if copay_match:
#         result["copay"] = copay_match.group(1).strip()
    
#     # Extract coinsurance
#     coin_match = re.search(r'(\d+%)[\s-]?coinsurance', cost_str)
#     if coin_match:
#         result["coinsurance"] = coin_match.group(1)
    
#     # Deductible note
#     if "deductible does not apply" in cost_str or "before deductible" in cost_str:
#         result["deductible_applies"] = False
#         result["notes"].append("deductible does not apply")
    
#     # Preauth in cost field (sometimes it's mixed)
#     if "preauthorization" in cost_str:
#         result["notes"].append("preauthorization required")
    
#     return result

def _benefit_service(chunk, E, R, A):
    event = _s(chunk.get("medical_event"))
    service = _s(chunk.get("service"))
    if not service:
        return

    net = _s(chunk.get("network_cost"))
    oon = _s(chunk.get("out_of_network_cost"))
    limits = _s(chunk.get("limitations"))
    requires_preauth = chunk.get("requires_preauth", False)

    E.add(PLAN_NODE)
    E.add(service)

    # ── EVENT STRUCTURE ─────────────────────────────
    if event:
        _add(E, R, PLAN_NODE, "HAS_MEDICAL_EVENT", event)
        _add(E, R, event, "INCLUDES_SERVICE", service)
    else:
        _add(E, R, PLAN_NODE, "HAS_BENEFIT_SERVICE", service)

    # ───────────────────────────────────────────────
    # NETWORK COST (STORE EXACT TEXT)
    # ───────────────────────────────────────────────
    if net:
        net_node = f"{service} | Network"
        _add(E, R, service, "HAS_NETWORK_COST", net_node)

        # ✅ ALWAYS store exact SBC text
        _add(E, R, net_node, "VALUE", net)

        # ✅ LIGHT detection (no parsing, just tagging)
        net_lower = net.lower()

        if "copay" in net_lower:
            copay_node = f"{service} | Network | Copay"
            _add(E, R, net_node, "HAS_COPAY", copay_node)
            _add(E, R, copay_node, "VALUE", net)

        if "coinsurance" in net_lower:
            coin_node = f"{service} | Network | Coinsurance"
            _add(E, R, net_node, "HAS_COINSURANCE", coin_node)
            _add(E, R, coin_node, "VALUE", net)

    # ───────────────────────────────────────────────
    # OUT-OF-NETWORK COST
    # ───────────────────────────────────────────────
    if oon:
        oon_node = f"{service} | OutOfNetwork"
        _add(E, R, service, "HAS_OUT_OF_NETWORK_COST", oon_node)

        # ✅ ALWAYS store exact SBC text
        _add(E, R, oon_node, "VALUE", oon)

        oon_lower = oon.lower()

        if "copay" in oon_lower:
            copay_node = f"{service} | OutOfNetwork | Copay"
            _add(E, R, oon_node, "HAS_COPAY", copay_node)
            _add(E, R, copay_node, "VALUE", oon)

        if "coinsurance" in oon_lower:
            coin_node = f"{service} | OutOfNetwork | Coinsurance"
            _add(E, R, oon_node, "HAS_COINSURANCE", coin_node)
            _add(E, R, coin_node, "VALUE", oon)

    # ───────────────────────────────────────────────
    # LIMITATIONS (STORE EXACT)
    # ───────────────────────────────────────────────
    if limits:
        lim_node = f"{service} | Limitation"
        _add(E, R, service, "HAS_LIMITATION", lim_node)
        _add(E, R, lim_node, "TEXT", limits)

    # ───────────────────────────────────────────────
    # PREAUTH
    # ───────────────────────────────────────────────
    combined_text = f"{net} {oon} {limits}".lower()

    if requires_preauth or "preauthorization" in combined_text:
        _add(E, R, service, "REQUIRES", "Preauthorization")

# def _benefit_service(chunk, E, R, A):
#     event   = _s(chunk.get("medical_event"))
#     service = _s(chunk.get("service"))

#     net     = _s(chunk.get("network_cost"))
#     oon     = _s(chunk.get("out_of_network_cost"))
#     limits  = _s(chunk.get("limitations"))
#     preauth = chunk.get("requires_preauth", False)
#     copay   = _s(chunk.get("copay"))
#     coins   = _s(chunk.get("coinsurance"))

#     if not service:
#         return

#     E.add(PLAN_NODE)
#     E.add(service)

#     # ── EVENT STRUCTURE ─────────────────────────────
#     if event:
#         _add(E, R, PLAN_NODE, "HAS_MEDICAL_EVENT", event)
#         _add(E, R, event, "INCLUDES_SERVICE", service)
#     else:
#         _add(E, R, PLAN_NODE, "HAS_BENEFIT_SERVICE", service)

#     # ── COST → NODE (IMPORTANT UPGRADE) ─────────────
#     if net:
#         cost_node = f"{service} | NetworkCost"
#         _add(E, R, service, "HAS_COST", cost_node)
#         _add_attr(A, cost_node, "type", "network")
#         _add_attr(A, cost_node, "value", net)

#     if oon:
#         cost_node = f"{service} | OutOfNetworkCost"
#         _add(E, R, service, "HAS_COST", cost_node)
#         _add_attr(A, cost_node, "type", "out_of_network")
#         _add_attr(A, cost_node, "value", oon)

#     # ── LIMITATIONS → NODE ─────────────────────────
#     if limits:
#         lim_node = f"{service} | Limitation"
#         _add(E, R, service, "HAS_LIMITATION", lim_node)
#         _add_attr(A, lim_node, "text", limits)

#     # ── PREAUTH → NODE ─────────────────────────────
#     if preauth:
#         _add(E, R, service, "REQUIRES", "Preauthorization")

#     # ── COPAY / COINSURANCE → NODE ────────────────
#     if copay:
#         copay_node = f"{service} | Copay"
#         _add(E, R, service, "HAS_COPAY", copay_node)
#         _add_attr(A, copay_node, "value", copay)

#     if coins:
#         coin_node = f"{service} | Coinsurance"
#         _add(E, R, service, "HAS_COINSURANCE", coin_node)
#         _add_attr(A, coin_node, "value", coins)


# ─────────────────────────────
# EXCLUDED SERVICE
# ─────────────────────────────

def _excluded_service(chunk, E, R, A):
    svc = _s(chunk.get("service"))
    if svc:
        _add(E, R, PLAN_NODE, "EXCLUDES_SERVICE", svc)


# ─────────────────────────────
# OTHER COVERED SERVICE
# ─────────────────────────────

def _other_covered_service(chunk, E, R, A):
    svc = _s(chunk.get("service"))
    if svc:
        _add(E, R, PLAN_NODE, "COVERS_SERVICE", svc)

# ─────────────────────────────
# COVERAGE EXAMPLE (SEMANTIC UPGRADE)
# ─────────────────────────────

def _coverage_example(chunk, E, R, A):

    name = _s(chunk.get("name"))
    if not name:
        return

    E.add(PLAN_NODE)

    text = name.lower()

    # ---------------------------------------------------
    # 1. CREATE GLOBAL GROUP NODE
    # ---------------------------------------------------
    group_node = "Coverage Example Scenarios"
    _add(E, R, PLAN_NODE, "INCLUDES_COVERAGE_EXAMPLES", group_node)

    # ---------------------------------------------------
    # 2. MAP SCENARIO TYPE
    # ---------------------------------------------------
    if any(k in text for k in ["peg", "baby", "maternity"]):
        scenario = "Pregnancy & Childbirth Scenario"
        category = "MATERNITY"

    elif any(k in text for k in ["joe", "diabetes"]):
        scenario = "Chronic Disease Management Scenario"
        category = "CHRONIC_CARE"

    elif any(k in text for k in ["mia", "fracture", "emergency"]):
        scenario = "Emergency Care Scenario"
        category = "EMERGENCY_CARE"

    else:
        scenario = name
        category = "GENERAL"

    # ---------------------------------------------------
    # 3. CONNECT GROUP → SCENARIO
    # ---------------------------------------------------
    _add(E, R, group_node, "HAS_SCENARIO", scenario)
    _add_attr(A, scenario, "category", category)

    # ---------------------------------------------------
    # 4. COST SUMMARY
    # ---------------------------------------------------
    total_cost = chunk.get("total_cost")
    patient_pays = chunk.get("patient_total")

    if total_cost:
        _add_attr(A, scenario, "total_example_cost", total_cost)

    if patient_pays:
        _add_attr(A, scenario, "patient_responsibility", patient_pays)

    # ---------------------------------------------------
    # 5. COST BREAKDOWN (STRUCTURED ENTITIES)
    # ---------------------------------------------------
    for k, v in (chunk.get("cost_breakdown") or {}).items():

        if not k or not v:
            continue

        cost_node = f"{scenario}::{k}"

        k_low = k.lower()

        if "deductible" in k_low:
            rel = "HAS_DEDUCTIBLE_COST"

        elif "copay" in k_low:
            rel = "HAS_COPAYMENT_COST"

        elif "coinsurance" in k_low:
            rel = "HAS_COINSURANCE_COST"

        elif "limit" in k_low or "exclusion" in k_low:
            rel = "HAS_LIMITATION"

        else:
            rel = "HAS_COST_COMPONENT"

        _add(E, R, scenario, rel, cost_node)
        _add_attr(A, cost_node, "amount", v)

    # ---------------------------------------------------
    # 6. SERVICES (IMPORTANT FIX)
    # ---------------------------------------------------
    for svc in (chunk.get("included_services") or []):

        svc = _s(svc)
        if not svc:
            continue

        _add(E, R, scenario, "COVERS_SERVICE", svc)

    # ---------------------------------------------------
    # 7. MARK SCENARIO TYPE RELATIONSHIP
    # ---------------------------------------------------
    _add(
        E,
        R,
        group_node,
        "HAS_COVERAGE_TYPE",
        category
    )


# ─────────────────────────────
# SEMANTIC SECTION DETECTION
# ─────────────────────────────

def _section(chunk, E, R, A):

    title = _s(chunk.get("title"))
    content = _s(chunk.get("content"))

    if not title and not content:
        return

    E.add(PLAN_NODE)

    raw_text = (f"{title} {content}").lower()
    text = re.sub(r"[^a-z0-9\s]", " ", raw_text)
    text = re.sub(r"\s+", " ", raw_text).strip()

    # ─────────────────────────
    # CONTINUATION RIGHTS
    # ─────────────────────────

    if (
        "your rights to continue coverage" in text
    ):

        node = "Rights to Continue Coverage"

        _add(
            E,
            R,
            PLAN_NODE,
            "PROVIDES_CONTINUATION_OF_COVERAGE_RIGHTS",
            node
        )

    # ─────────────────────────
    # GRIEVANCE / APPEALS
    # ─────────────────────────

    elif (
        "grievance" in text
        or "appeal" in text
        or "claim denial" in text
    ):

        node = "Grievance and Appeals Rights"

        _add(
            E,
            R,
            PLAN_NODE,
            "PROVIDES_GRIEVANCE_AND_APPEAL_RIGHTS",
            node
        )

    # ─────────────────────────
    # MINIMUM ESSENTIAL COVERAGE
    # ─────────────────────────

    elif "minimum essential coverage" in text:

        node = "Minimum Essential Coverage"

        _add(
            E,
            R,
            PLAN_NODE,
            "SATISFIES_MINIMUM_ESSENTIAL_COVERAGE_REQUIREMENT",
            node
        )

    # ─────────────────────────
    # MINIMUM VALUE STANDARD
    # ─────────────────────────

    elif "minimum value standards" in text:

        node = "Minimum Value Standards"

        _add(
            E,
            R,
            PLAN_NODE,
            "SATISFIES_MINIMUM_VALUE_STANDARD",
            node
        )

    # ─────────────────────────
    # LANGUAGE ACCESS
    # ─────────────────────────

    elif (
        "language access" in text
        or "spanish" in text
        or "tagalog" in text
        or "chinese" in text
        or "navajo" in text
    ):

        node = "Language Assistance Services"

        _add(
            E,
            R,
            PLAN_NODE,
            "PROVIDES_LANGUAGE_ASSISTANCE_SERVICES",
            node
        )

    # ─────────────────────────
    # COVERAGE EXAMPLES
    # ─────────────────────────

    elif (
        "coverage example" in text
        or "peg is having a baby" in text
        or "managing joe" in text
        or "mia's simple fracture" in text
    ):

        node = "Health Coverage Cost Examples"

        _add(
            E,
            R,
            PLAN_NODE,
            "PROVIDES_HEALTH_COVERAGE_COST_EXAMPLES",
            node
        )

    # ─────────────────────────
    # COVERAGE DISCLAIMER
    # ─────────────────────────

    elif (
        "not a cost estimator" in text
        or "actual costs will be different" in text
    ):

        node = "Coverage Example Disclaimer"

        _add(
            E,
            R,
            PLAN_NODE,
            "PROVIDES_COVERAGE_COST_DISCLAIMER",
            node
        )

    else:
        # Skip vague sections completely
        return

    if content:
        _add_attr(A, node, "summary", content[:800])


# ─────────────────────────────
# PREAMBLE
# ─────────────────────────────

def _preamble(chunk, E, R, A):

    content = _s(chunk.get("content"))

    if not content:
        return

    node = "Plan Overview"

    _add(
        E,
        R,
        PLAN_NODE,
        "PROVIDES_PLAN_OVERVIEW",
        node
    )

    _add_attr(A, node, "summary", content[:1000])


# ─────────────────────────────
# FOOTNOTE
# ─────────────────────────────

def _footnote(chunk, E, R, A):

    content = _s(chunk.get("content"))

    if not content:
        return

    text = (content)

    E.add(PLAN_NODE)

    # ─────────────────────────
    # WELLNESS PROGRAM
    # ─────────────────────────

    if "wellness program" in text:

        node = "Wellness Program Cost Reduction Notice"

        _add(
            E,
            R,
            PLAN_NODE,
            "OFFERS_WELLNESS_PROGRAM_SAVINGS",
            node
        )

    # ─────────────────────────
    # COVERAGE ASSUMPTION
    # ─────────────────────────

    elif (
        "examples assume" in text
        or "these numbers assume" in text
    ):

        node = "Coverage Example Assumptions"

        _add(
            E,
            R,
            PLAN_NODE,
            "PROVIDES_COVERAGE_EXAMPLE_ASSUMPTIONS",
            node
        )

    # ─────────────────────────
    # COST DISCLAIMER
    # ─────────────────────────

    elif (
        "not a cost estimator" in text
        or "actual costs" in text
    ):

        node = "Medical Cost Estimation Disclaimer"

        _add(
            E,
            R,
            PLAN_NODE,
            "DISCLAIMS_EXACT_MEDICAL_COST_ESTIMATES",
            node
        )

    else:
        return

    _add_attr(A, node, "content", content[:800]) # Keep reasonable length

# ─────────────────────────────
# DISPATCHER
# ─────────────────────────────

_DISPATCH = {
    "plan_metadata": _plan_metadata,
    "important_question": _important_question,
    "benefit_service": _benefit_service,
    "excluded_service": _excluded_service,
    "other_covered_service": _other_covered_service,
    "coverage_example": _coverage_example,
    "section": _section,
    "preamble": _preamble,
    "footnote": _footnote,
}


# ─────────────────────────────
# MAIN FUNCTION
# ─────────────────────────────

def chunks_to_graph_data(chunks: list[dict]) -> dict:
    entities = set()
    relationships = []
    attributes = []

    for chunk in chunks:
        fn = _DISPATCH.get(chunk.get("type"))
        if fn:
            fn(chunk, entities, relationships, attributes)

    return {
        "entities": sorted(entities),
        "relationships": relationships,
        "attributes": attributes,
    }