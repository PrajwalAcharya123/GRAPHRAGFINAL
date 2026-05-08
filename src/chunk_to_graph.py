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
# """safe attribute builder"""
# if entity and value:
# A.append((entity, key, value))
def _add_attr(A, entity, key, value):
    if not entity:
        return
    if value is None:
        return
    v = str(value).strip()
    if v == "":
        return
    A.append((entity, key, v))

def extract_copay_value(text):
    if not text:
        return None

    match = re.search(r"\$\s*\d+", text)
    return match.group(0).replace(" ", "") if match else None

def extract_coinsurance_value(text):
    if not text:
        return None

    match = re.search(r"\d+\s*%", text)
    return match.group(0).replace(" ", "") if match else None
# ─────────────────────────────
# PLAN METADATA
# ─────────────────────────────
def _plan_metadata(chunk, E, R, A):
    E.add(PLAN_NODE)
    cov = _s(chunk.get("coverage_for"))
    pt = _s(chunk.get("plan_type"))
    if cov:
        _add(E, R, PLAN_NODE, "COVERS", cov)
    if pt:
        _add_attr(A, PLAN_NODE, "plan_type", pt)
# ─────────────────────────────
# IMPORTANT QUESTION
# ─────────────────────────────
# def _important_question(chunk, E, R, A):
# q = _s(chunk.get("question"))
# if not q:
# return
# node = f"IQ: {q[:80]}" if len(q) > 80 else q
# _add(E, R, PLAN_NODE, "HAS_IMPORTANT_QUESTION", node)
# _add_attr(A, node, "question", q)
# _add_attr(A, node, "answer", chunk.get("answer"))
# _add_attr(A, node, "why_it_matters", chunk.get("why_it_matters"))
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
# """Smart parser for cost descriptions"""
# if not cost_str or cost_str.strip() == "":
# return {}
   
# cost_str = cost_str.lower().strip()
# result = {
# "raw": cost_str,
# "copay": None,
# "coinsurance": None,
# "deductible_applies": True,
# "notes": []
# }
   
# # Extract copay
# copay_match = re.search(r'(\$\d+[\s-]?(?:copay|per visit|per test|per day|office visit))', cost_str)
# if copay_match:
# result["copay"] = copay_match.group(1).strip()
   
# # Extract coinsurance
# coin_match = re.search(r'(\d+%)[\s-]?coinsurance', cost_str)
# if coin_match:
# result["coinsurance"] = coin_match.group(1)
   
# # Deductible note
# if "deductible does not apply" in cost_str or "before deductible" in cost_str:
# result["deductible_applies"] = False
# result["notes"].append("deductible does not apply")
   
# # Preauth in cost field (sometimes it's mixed)
# if "preauthorization" in cost_str:
# result["notes"].append("preauthorization required")
   
# return result
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
        # ALWAYS store exact SBC text
        _add(E, R, net_node, "VALUE", net)
        # LIGHT detection (no parsing, just tagging)
        net_lower = net.lower()
        if "copay" in net_lower:
            copay_value = extract_copay_value(net)
            copay_node = f"{service} | Network | Copay"
            _add(E, R, net_node, "HAS_COPAY", copay_node)
            if copay_value:
                _add_attr(A, copay_node, "copay_value", copay_value)
        if "coinsurance" in net_lower:
            coin_value = extract_coinsurance_value(net)
            coin_node = f"{service} | Network | Coinsurance"
            _add(E, R, net_node, "HAS_COINSURANCE", coin_node)
            # _add(E, R, coin_node, "VALUE", net)
            if coin_value:
                _add_attr(A, coin_node, "coinsurance_value", coin_value)

    # OUT-OF-NETWORK COST
    if oon:
        oon_node = f"{service} | OutOfNetwork"
        _add(E, R, service, "HAS_OUT_OF_NETWORK_COST", oon_node)
        #  ALWAYS store exact SBC text
        _add(E, R, oon_node, "VALUE", oon)
        oon_lower = oon.lower()
        if "copay" in oon_lower:
            copay_value = extract_copay_value(oon)
            copay_node = f"{service} | OutOfNetwork | Copay"
            _add(E, R, oon_node, "HAS_COPAY", copay_node)
            # _add(E, R, copay_node, "VALUE", oon)
            if copay_value:
                _add_attr(A, copay_node, "copay_value", copay_value)
        if "coinsurance" in oon_lower:
            coin_value = extract_coinsurance_value(oon)
            coin_node = f"{service} | OutOfNetwork | Coinsurance"
            _add(E, R, oon_node, "HAS_COINSURANCE", coin_node)
            # _add(E, R, coin_node, "VALUE", oon)
            if coin_value:
                _add_attr(A, coin_node, "coinsurance_value", coin_value)
  
    # LIMITATIONS 
  
    if limits:
        lim_node = f"{service} | Limitation"
        _add(E, R, service, "HAS_LIMITATION", lim_node)
        _add(E, R, lim_node, "TEXT", limits)

    # PREAUTH

    combined_text = f"{net} {oon} {limits}".lower()
    if requires_preauth or "preauthorization" in combined_text:
        _add(E, R, service, "REQUIRES", "Preauthorization")
# def _benefit_service(chunk, E, R, A):
# event = _s(chunk.get("medical_event"))
# service = _s(chunk.get("service"))
# net = _s(chunk.get("network_cost"))
# oon = _s(chunk.get("out_of_network_cost"))
# limits = _s(chunk.get("limitations"))
# preauth = chunk.get("requires_preauth", False)
# copay = _s(chunk.get("copay"))
# coins = _s(chunk.get("coinsurance"))
# if not service:
# return
# E.add(PLAN_NODE)
# E.add(service)
# # ── EVENT STRUCTURE ─────────────────────────────
# if event:
# _add(E, R, PLAN_NODE, "HAS_MEDICAL_EVENT", event)
# _add(E, R, event, "INCLUDES_SERVICE", service)
# else:
# _add(E, R, PLAN_NODE, "HAS_BENEFIT_SERVICE", service)
# # ── COST → NODE (IMPORTANT UPGRADE) ─────────────
# if net:
# cost_node = f"{service} | NetworkCost"
# _add(E, R, service, "HAS_COST", cost_node)
# _add_attr(A, cost_node, "type", "network")
# _add_attr(A, cost_node, "value", net)
# if oon:
# cost_node = f"{service} | OutOfNetworkCost"
# _add(E, R, service, "HAS_COST", cost_node)
# _add_attr(A, cost_node, "type", "out_of_network")
# _add_attr(A, cost_node, "value", oon)
# # ── LIMITATIONS → NODE ─────────────────────────
# if limits:
# lim_node = f"{service} | Limitation"
# _add(E, R, service, "HAS_LIMITATION", lim_node)
# _add_attr(A, lim_node, "text", limits)
# # ── PREAUTH → NODE ─────────────────────────────
# if preauth:
# _add(E, R, service, "REQUIRES", "Preauthorization")
# # ── COPAY / COINSURANCE → NODE ────────────────
# if copay:
# copay_node = f"{service} | Copay"
# _add(E, R, service, "HAS_COPAY", copay_node)
# _add_attr(A, copay_node, "value", copay)
# if coins:
# coin_node = f"{service} | Coinsurance"
# _add(E, R, service, "HAS_COINSURANCE", coin_node)
# _add_attr(A, coin_node, "value", coins)
# ─────────────────────────────
# EXCLUDED SERVICE
# ─────────────────────────────
def _excluded_service(chunk, E, R, A):
    svc = _s(chunk.get("service"))
    if svc:
        _add(E, R, PLAN_NODE, "EXCLUDES_SERVICE", svc)

# OTHER COVERED SERVICE

def _other_covered_service(chunk, E, R, A):
    svc = _s(chunk.get("service"))
    if svc:
        _add(E, R, PLAN_NODE, "COVERS_SERVICE", svc)

# COVERAGE EXAMPLES 
def _coverage_example(all_chunks, E, R, A):
    """
    Builds a rich semantic graph from normalized coverage example chunks.
    Preserves:
    - scenario identity
    - subtitles
    - services
    - plan parameters
    - total costs
    - patient responsibility
    - section headers
    - exclusions
    - cost-sharing structure
    """
    E.add(PLAN_NODE)
    # ---------------------------------------------------
    # ROOT GROUP
    # ---------------------------------------------------
    root = "Coverage Example Scenarios"
    _add(
        E,
        R,
        PLAN_NODE,
        "INCLUDES_COVERAGE_EXAMPLES",
        root
    )
    current_example = None
    current_section = None
    processed = set()
    # ---------------------------------------------------
    # SCENARIO MAPPER
    # ---------------------------------------------------
    def map_scenario(name):
        low = name.lower()
        if any(x in low for x in ["peg", "baby", "pregnancy", "childbirth"]):
            return (
                "Pregnancy & Childbirth Scenario",
                "MATERNITY"
            )
        elif any(x in low for x in ["joe", "diabetes"]):
            return (
                "Chronic Disease Management Scenario",
                "CHRONIC_CARE"
            )
        elif any(x in low for x in ["mia", "fracture", "emergency"]):
            return (
                "Emergency Care Scenario",
                "EMERGENCY_CARE"
            )
        return (name, "GENERAL")
    # ---------------------------------------------------
    # MAIN LOOP
    # ---------------------------------------------------
    for chunk in all_chunks:
        if not isinstance(chunk, dict):
            continue
        ctype = chunk.get("type", "")
        # =================================================
        # ABOUT SECTION
        # =================================================
        if ctype == "coverage_about":
            txt = _s(chunk.get("content"))
            if txt:
                _add_attr(
                    A,
                    root,
                    "about_coverage_examples",
                    txt
                )
            continue
        # =================================================
        # FOOTNOTE
        # =================================================
        if ctype == "footnote":
            txt = _s(chunk.get("content"))
            if txt:
                foot = "Coverage Example Footnote"
                _add(E, R, root, "HAS_FOOTNOTE", foot)
                _add_attr(A, foot, "text", txt)
            continue
        # =================================================
        # SCENARIO DETECTION
        # =================================================
        ex_name = _s(chunk.get("example_name"))
        if ex_name:
            scenario, category = map_scenario(ex_name)
            if current_example != scenario:
                current_example = scenario
                current_section = None
                if scenario not in processed:
                    processed.add(scenario)
                    _add(
                        E,
                        R,
                        root,
                        "HAS_SCENARIO",
                        scenario
                    )
                    _add_attr(
                        A,
                        scenario,
                        "category",
                        category
                    )
                    _add_attr(
                        A,
                        scenario,
                        "display_name",
                        ex_name
                    )
        if not current_example:
            continue
        # =================================================
        # SUBTITLE
        # =================================================
        if ctype == "coverage_subtitle":
            subtitle = _s(chunk.get("content"))
            if subtitle:
                _add_attr(
                    A,
                    current_example,
                    "description",
                    subtitle
                )
            continue
        # =================================================
        # SECTION HEADERS
        # =================================================
        if ctype == "coverage_section_header":
            section_name = _s(chunk.get("content"))
            if not section_name:
                continue
            current_section = (
                f"{current_example} | {section_name}"
            )
            _add(
                E,
                R,
                current_example,
                "HAS_SECTION",
                current_section
            )
            _add_attr(
                A,
                current_section,
                "title",
                section_name
            )
            continue
        # =================================================
        # SERVICES
        # =================================================
        if ctype == "coverage_service":
            svc = _s(chunk.get("service"))
            if not svc:
                continue
            service_node = svc
            _add(
                E,
                R,
                current_example,
                "COVERS_SERVICE",
                service_node
            )
            # Optional semantic typing
            low = svc.lower()
            if "diagnostic" in low:
                _add(
                    E,
                    R,
                    service_node,
                    "SERVICE_CATEGORY",
                    "Diagnostic Services"
                )
            elif "emergency" in low:
                _add(
                    E,
                    R,
                    service_node,
                    "SERVICE_CATEGORY",
                    "Emergency Services"
                )
            elif "prescription" in low:
                _add(
                    E,
                    R,
                    service_node,
                    "SERVICE_CATEGORY",
                    "Prescription Drug Coverage"
                )
            elif "rehabilitation" in low:
                _add(
                    E,
                    R,
                    service_node,
                    "SERVICE_CATEGORY",
                    "Rehabilitation Services"
                )
            continue
        # =================================================
        # TOTAL COST
        # =================================================
        if ctype == "coverage_total_cost":
            val = _s(chunk.get("value"))
            if val:
                total_node = (
                    f"{current_example} | Total Example Cost"
                )
                _add(
                    E,
                    R,
                    current_example,
                    "HAS_TOTAL_EXAMPLE_COST",
                    total_node
                )
                _add_attr(
                    A,
                    total_node,
                    "amount",
                    val
                )
            continue
        # =================================================
        # PARAMETERS + COST SHARING
        # =================================================
        if ctype in (
            "coverage_parameter",
            "coverage_cost_sharing"
        ):
            key = _s(chunk.get("key"))
            val = _s(chunk.get("value"))
            if not key or not val:
                continue
            low = key.lower()
            component = (
                f"{current_example} | {key}"
            )
            # --------------------------------------------
            # RELATION TYPE
            # --------------------------------------------
            if "deductible" in low:
                rel = "HAS_DEDUCTIBLE"
            elif "copay" in low:
                rel = "HAS_COPAYMENT"
            elif "coinsurance" in low:
                rel = "HAS_COINSURANCE"
            elif "limit" in low or "exclusion" in low:
                rel = "HAS_LIMITATION"
            elif "total" in low and "pay" in low:
                rel = "HAS_PATIENT_RESPONSIBILITY"
                _add_attr(
                    A,
                    current_example,
                    "patient_total",
                    val
                )
            else:
                rel = "HAS_COST_COMPONENT"
            # --------------------------------------------
            # CONNECT
            # --------------------------------------------
            _add(
                E,
                R,
                current_example,
                rel,
                component
            )
            # --------------------------------------------
            # SECTION ORGANIZATION
            # --------------------------------------------
            if current_section:
                _add(
                    E,
                    R,
                    current_section,
                    "CONTAINS_COMPONENT",
                    component
                )
            # --------------------------------------------
            # ATTRIBUTES
            # --------------------------------------------
            _add_attr(
                A,
                component,
                "description",
                key
            )
            _add_attr(
                A,
                component,
                "amount",
                val
            )
    print(
        f" → Coverage Examples Graph built successfully "
        f"({len(processed)} scenarios)"
    )


# SEMANTIC SECTION DETECTION
# ─────────────────────────────
def _section(chunk, E, R, A):
    title = _s(chunk.get("title", ""))
    content = _s(chunk.get("content", ""))
    if not title and not content:
        return

    raw_text = f"{title} {content}".lower()
    text = re.sub(r"\s+", " ", raw_text).strip()

    E.add(PLAN_NODE)

    added = False

    # ─────────────────────────
    # CONTINUATION RIGHTS (Made more robust)
    # ─────────────────────────
    if any(phrase in text for phrase in [
        "your rights to continue coverage",
        "right to continue coverage",
        "continuation of coverage",
        "continue coverage",
        "cobra"  # common real-world term
    ]):
        node = "Rights to Continue Coverage"
        _add(E, R, PLAN_NODE, "PROVIDES_CONTINUATION_OF_COVERAGE_RIGHTS", node)
        added = True

    # ─────────────────────────
    # GRIEVANCE / APPEALS
    # ─────────────────────────
    elif any(phrase in text for phrase in [
        "grievance", "appeal", "claim denial", "internal appeal", "external review"
    ]):
        node = "Grievance and Appeals Rights"
        _add(E, R, PLAN_NODE, "PROVIDES_GRIEVANCE_AND_APPEAL_RIGHTS", node)
        added = True

    # ─────────────────────────
    # MINIMUM ESSENTIAL COVERAGE
    # ─────────────────────────
    elif "minimum essential coverage" in text:
        node = "Minimum Essential Coverage"
        _add(E, R, PLAN_NODE, "SATISFIES_MINIMUM_ESSENTIAL_COVERAGE_REQUIREMENT", node)
        added = True

    # ─────────────────────────
    # MINIMUM VALUE STANDARD
    # ─────────────────────────
    elif any(phrase in text for phrase in ["minimum value standard", "minimum value"]):
        node = "Minimum Value Standards"
        _add(E, R, PLAN_NODE, "SATISFIES_MINIMUM_VALUE_STANDARD", node)
        added = True

    # ─────────────────────────
    # LANGUAGE ACCESS
    # ─────────────────────────
    elif any(phrase in text for phrase in [
        "language access", "language assistance", "spanish", "tagalog", "chinese", "navajo"
    ]):
        node = "Language Assistance Services"
        _add(E, R, PLAN_NODE, "PROVIDES_LANGUAGE_ASSISTANCE_SERVICES", node)
        added = True

    # ─────────────────────────
    # COVERAGE EXAMPLES
    # ─────────────────────────
    elif any(phrase in text for phrase in [
        "coverage example", "peg is having", "managing joe", "mia's simple fracture"
    ]):
        node = "Health Coverage Cost Examples"
        _add(E, R, PLAN_NODE, "PROVIDES_HEALTH_COVERAGE_COST_EXAMPLES", node)
        added = True

    # ─────────────────────────
    # COVERAGE DISCLAIMER
    # ─────────────────────────
    elif any(phrase in text for phrase in [
        "not a cost estimator", "actual costs will be different", "this is only a summary"
    ]):
        node = "Coverage Example Disclaimer"
        _add(E, R, PLAN_NODE, "PROVIDES_COVERAGE_COST_DISCLAIMER", node)
        added = True

    # Add more common important sections here (expand as needed)
    elif "your rights" in text and "plan" in text:
        node = "Plan Rights and Responsibilities"
        _add(E, R, PLAN_NODE, "PROVIDES_MEMBER_RIGHTS", node)
        added = True

    if added and content:
        _add_attr(A, node, "summary", content[:800])

    # Optional: Log when nothing matched (very useful for debugging)
    # else:
    #     print(f"[DEBUG] Section skipped: {title[:60]}")
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
    # "coverage_example": _coverage_example,
    "section": _section,
    "preamble": _preamble,
    "footnote": _footnote,
}
# ─────────────────────────────
# MAIN FUNCTION
# ─────────────────────────────
# def chunks_to_graph_data(chunks: list[dict]) -> dict:
# entities = set()
# relationships = []
# attributes = []
# coverage_chunks = [
# c for c in chunks
# if c.get("type", "").startswith("coverage_")
# ]
# if coverage_chunks:
# _coverage_example(
# coverage_chunks,
# entities,
# relationships,
# attributes
# )
# for chunk in chunks:
# fn = _DISPATCH.get(chunk.get("type"))
# if fn:
# fn(chunk, entities, relationships, attributes)
# return {
# "entities": sorted(entities),
# "relationships": relationships,
# "attributes": attributes,
# }
def chunks_to_graph_data(chunks):
    entities = set()
    relationships = []
    attributes = []
    # 1. Run coverage pipeline FIRST (isolated)
    coverage_chunks = [
        c for c in chunks
        if c.get("type", "").startswith("coverage_")
    ]
    if coverage_chunks:
        _coverage_example(coverage_chunks, entities, relationships, attributes)
    # 2. Run everything else (clean separation)
    for chunk in chunks:
        ctype = chunk.get("type")
        if ctype.startswith("coverage_"):
            continue
        fn = _DISPATCH.get(ctype)
        if fn:
            fn(chunk, entities, relationships, attributes)
    return {
        "entities": sorted(entities),
        "relationships": relationships,
        "attributes": attributes,
    } 