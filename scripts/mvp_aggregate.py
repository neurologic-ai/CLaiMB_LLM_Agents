# #!/usr/bin/env python3
# from __future__ import annotations
# import argparse, json, csv, re
# from pathlib import Path
# from typing import Dict, Tuple, Any

# # ------------------------------------------------------------
# # 1) EXACT mapping from your 75 subsections -> MVP (8 cats, 24 subcats)
# #    This covers all 75; only the ones present in your 51 will roll up.
# # ------------------------------------------------------------

# MVP = {
#     "01. Technical Infrastructure": ["Cloud Capabilities","Computing Resources","Development Environment"],
#     "02. Data Management & Quality": ["Data Architecture","Data Quality","Data Governance"],
#     "03. AI/ML Capabilities": ["Model Development","Production Deployment","MLOps Maturity"],
#     "04. Business Integration": ["Strategic Alignment","Use Case Implementation","ROI Measurement"],
#     "05. Governance & Risk Management": ["Ethical Framework","Regulatory Compliance","Risk Assessment"],
#     "06. Talent & Skills": ["Technical Expertise","Domain Knowledge","Team Structure"],
#     "07. Innovation & Research": ["R&D Investment","Innovation Pipeline","External Partnerships"],
#     "08. Cultural Readiness": ["Change Management","Collaboration Culture","Learning Environment"],
# }

# SUBSECTION15_TO_MVP: Dict[str, Tuple[str, str]] = {
#     # 01 Technical Infrastructure
#     "1.1 Cloud Computing Capabilities": ("01. Technical Infrastructure","Cloud Capabilities"),
#     "1.2 Computing Resources": ("01. Technical Infrastructure","Computing Resources"),
#     "1.3 Development Environment": ("01. Technical Infrastructure","Development Environment"),
#     "1.4 Integration Architecture": ("01. Technical Infrastructure","Cloud Capabilities"),
#     "1.5 Security Infrastructure": ("01. Technical Infrastructure","Computing Resources"),
#     # 02 Data Management & Quality
#     "2.1 Data Architecture": ("02. Data Management & Quality","Data Architecture"),
#     "2.2 Data Quality": ("02. Data Management & Quality","Data Quality"),
#     "2.3 Data Governance": ("02. Data Management & Quality","Data Governance"),
#     "2.4 Data Operations": ("02. Data Management & Quality","Data Architecture"),
#     "2.5 Data Accessibility": ("02. Data Management & Quality","Data Governance"),
#     # 03 AI/ML Capabilities
#     "3.1 Model Development": ("03. AI/ML Capabilities","Model Development"),
#     "3.2 Production Deployment": ("03. AI/ML Capabilities","Production Deployment"),
#     "3.3 MLOps Maturity": ("03. AI/ML Capabilities","MLOps Maturity"),
#     "3.4 Model Governance": ("03. AI/ML Capabilities","MLOps Maturity"),
#     "3.5 Advanced Capabilities": ("03. AI/ML Capabilities","Model Development"),
#     # 04 Talent & Skills  -> MVP 06
#     "4.1 Technical Expertise": ("06. Talent & Skills","Technical Expertise"),
#     "4.2 Domain Knowledge": ("06. Talent & Skills","Domain Knowledge"),
#     "4.3 Team Structure": ("06. Talent & Skills","Team Structure"),
#     "4.4 Training & Development": ("06. Talent & Skills","Technical Expertise"),
#     "4.5 Recruitment & Retention": ("06. Talent & Skills","Team Structure"),
#     # 05 Governance & Ethics -> MVP 05
#     "5.1 Ethical Framework": ("05. Governance & Risk Management","Ethical Framework"),
#     "5.2 Regulatory Compliance": ("05. Governance & Risk Management","Regulatory Compliance"),
#     "5.3 Risk Management": ("05. Governance & Risk Management","Risk Assessment"),
#     "5.4 Accountability Structure": ("05. Governance & Risk Management","Ethical Framework"),
#     "5.5 Transparency Practices": ("05. Governance & Risk Management","Ethical Framework"),
#     # 06 Strategic Alignment -> MVP 04
#     "6.1 Business Integration": ("04. Business Integration","Strategic Alignment"),
#     "6.2 Leadership Support": ("04. Business Integration","Strategic Alignment"),
#     "6.3 Investment Strategy": ("04. Business Integration","Strategic Alignment"),
#     "6.4 Innovation Management": ("04. Business Integration","Use Case Implementation"),
#     "6.5 Partnership Ecosystem": ("04. Business Integration","Use Case Implementation"),
#     # 07 Cultural Readiness -> MVP 08
#     "7.1 Innovation Mindset": ("08. Cultural Readiness","Learning Environment"),
#     "7.2 Change Management": ("08. Cultural Readiness","Change Management"),
#     "7.3 Collaboration Culture": ("08. Cultural Readiness","Collaboration Culture"),
#     "7.4 Decision Making": ("08. Cultural Readiness","Collaboration Culture"),
#     "7.5 Learning Environment": ("08. Cultural Readiness","Learning Environment"),
#     # 08 Process Maturity -> MVP 05 (operational controls)
#     "8.1 Project Management": ("05. Governance & Risk Management","Risk Assessment"),
#     "8.2 Documentation Practices": ("05. Governance & Risk Management","Regulatory Compliance"),
#     "8.3 Quality Assurance": ("05. Governance & Risk Management","Risk Assessment"),
#     "8.4 Operational Excellence": ("05. Governance & Risk Management","Risk Assessment"),
#     "8.5 Measurement & Metrics": ("05. Governance & Risk Management","Regulatory Compliance"),
#     # 09 Foundation Model Operations -> MVP 03
#     "9.1 Model Integration & Deployment": ("03. AI/ML Capabilities","Production Deployment"),
#     "9.2 Domain Adaptation & Fine-tuning": ("03. AI/ML Capabilities","Model Development"),
#     "9.3 Performance Optimization": ("03. AI/ML Capabilities","MLOps Maturity"),
#     "9.4 Risk & Compliance Management": ("05. Governance & Risk Management","Regulatory Compliance"),
#     "9.5 Scaling & Distribution": ("03. AI/ML Capabilities","Production Deployment"),
#     # 10 Generative AI Capabilities -> MVP 03
#     "10.1 Multi-Modal Generation": ("03. AI/ML Capabilities","Model Development"),
#     "10.2 Quality Control & Validation": ("03. AI/ML Capabilities","MLOps Maturity"),
#     "10.3 Creative Workflow Integration": ("03. AI/ML Capabilities","Production Deployment"),
#     "10.4 Custom Generation Control": ("03. AI/ML Capabilities","Model Development"),
#     "10.5 Domain-Specific Generation": ("03. AI/ML Capabilities","Model Development"),
#     # 11 Responsible AI & Social Impact -> MVP 05
#     "11.1 Algorithmic Fairness & Bias Mitigation": ("05. Governance & Risk Management","Ethical Framework"),
#     "11.2 Explainability & Interpretability": ("05. Governance & Risk Management","Ethical Framework"),
#     "11.3 Privacy & Data Protection": ("05. Governance & Risk Management","Regulatory Compliance"),
#     "11.4 Societal Impact Assessment": ("05. Governance & Risk Management","Ethical Framework"),
#     "11.5 Human-AI Collaboration": ("08. Cultural Readiness","Collaboration Culture"),
#     # 12 AI Business Value & ROI -> MVP 04
#     "12.1 Revenue Generation & Growth": ("04. Business Integration","ROI Measurement"),
#     "12.2 Cost Reduction & Efficiency": ("04. Business Integration","ROI Measurement"),
#     "12.3 Customer Experience Enhancement": ("04. Business Integration","Use Case Implementation"),
#     "12.4 Innovation & Product Development": ("04. Business Integration","Use Case Implementation"),
#     "12.5 Competitive Advantage & Market Position": ("04. Business Integration","Strategic Alignment"),
#     # 13 AI Risk & Resilience -> MVP 05
#     "13.1 Model Reliability & Robustness": ("05. Governance & Risk Management","Risk Assessment"),
#     "13.2 Data Dependability & Trust": ("05. Governance & Risk Management","Risk Assessment"),
#     "13.3 Vendor & Technology Risk": ("05. Governance & Risk Management","Risk Assessment"),
#     "13.4 Operational Continuity": ("05. Governance & Risk Management","Risk Assessment"),
#     "13.5 Regulatory & Legal Compliance": ("05. Governance & Risk Management","Regulatory Compliance"),
#     # 14 AI Ecosystem & External Integration -> MVP 04 (and one to 07)
#     "14.1 Customer AI Integration": ("04. Business Integration","Use Case Implementation"),
#     "14.2 Supplier & Vendor AI Collaboration": ("04. Business Integration","Strategic Alignment"),
#     "14.3 Industry Standards & Consortiums": ("04. Business Integration","Strategic Alignment"),
#     "14.4 Research & Partnerships": ("07. Innovation & Research","External Partnerships"),
#     "14.5 Regulatory & Policy Engagement": ("04. Business Integration","Strategic Alignment"),
#     # 15 AI Leadership & Vision -> MVP 04
#     "15.1 AI Strategy & Roadmap": ("04. Business Integration","Strategic Alignment"),
#     "15.2 Executive AI Literacy": ("04. Business Integration","Strategic Alignment"),
#     "15.3 Organizational Transformation": ("04. Business Integration","Use Case Implementation"),
#     "15.4 Future-Proofing & Adaptability": ("04. Business Integration","Strategic Alignment"),
#     "15.5 Thought Leadership & Industry Influence": ("04. Business Integration","Strategic Alignment"),
# }

# # Default MVP weights (%)
# DEFAULT_WEIGHTS = {
#     "01. Technical Infrastructure": 20,
#     "02. Data Management & Quality": 15,
#     "03. AI/ML Capabilities": 20,
#     "04. Business Integration": 15,
#     "05. Governance & Risk Management": 10,
#     "06. Talent & Skills": 8,
#     "07. Innovation & Research": 7,
#     "08. Cultural Readiness": 5,
# }

# def parse_weights(s: str | None) -> Dict[str,float]:
#     if not s: return DEFAULT_WEIGHTS.copy()
#     aliases = {"TI":"01. Technical Infrastructure","DMQ":"02. Data Management & Quality",
#                "AI":"03. AI/ML Capabilities","BI":"04. Business Integration",
#                "GOV":"05. Governance & Risk Management","TS":"06. Talent & Skills",
#                "INNO":"07. Innovation & Research","CULT":"08. Cultural Readiness"}
#     out = DEFAULT_WEIGHTS.copy()
#     for part in s.split(","):
#         if "=" not in part: continue
#         k,v = part.split("=",1)
#         k=k.strip().upper(); v=float(v.strip())
#         if k in aliases: out[aliases[k]] = v
#     return out

# def load_aggregate(path: Path) -> Dict[str,Any]:
#     return json.loads(path.read_text(encoding="utf-8"))

# def rollup(agg: Dict[str,Any]) -> Dict[str,Any]:
#     subsections = agg["subsections"]  # { "X.Y Title": {... score, numerator, denominator ...} }

#     # Sub-category accumulators
#     sub_num: Dict[Tuple[str,str], float] = {}
#     sub_den: Dict[Tuple[str,str], float] = {}
#     sub_cnt: Dict[Tuple[str,str], int] = {}
#     unmapped = {}

#     for sub_label, row in subsections.items():
#         m = SUBSECTION15_TO_MVP.get(sub_label)
#         if not m:
#             unmapped[sub_label] = row
#             continue
#         cat, subcat = m
#         if subcat not in MVP[cat]:
#             raise ValueError(f"Invalid mapping {sub_label} -> ({cat}, {subcat})")
#         num = float(row["numerator"]); den = float(row["denominator"])
#         cnt = int(row.get("metric_contributions",0))
#         key = (cat, subcat)
#         sub_num[key] = sub_num.get(key,0.0) + num
#         sub_den[key] = sub_den.get(key,0.0) + den
#         sub_cnt[key] = sub_cnt.get(key,0) + cnt

#     # Build sub-category table
#     sub_table: Dict[str,Dict[str,Any]] = {}
#     for (cat, subcat), den in sub_den.items():
#         score = (sub_num[(cat,subcat)]/den) if den>0 else 0.0
#         sub_table[f"{cat} :: {subcat}"] = {
#             "score": round(score,2),
#             "numerator": round(sub_num[(cat,subcat)],2),
#             "denominator": round(den,2),
#             "metric_contributions": sub_cnt[(cat,subcat)],
#         }

#     # Roll to category level (evidence-weighted)
#     cat_num: Dict[str,float] = {}
#     cat_den: Dict[str,float] = {}
#     for key,row in sub_table.items():
#         cat = key.split(" :: ")[0]
#         cat_num[cat] = cat_num.get(cat,0.0) + row["numerator"]
#         cat_den[cat] = cat_den.get(cat,0.0) + row["denominator"]

#     cat_table: Dict[str,Dict[str,Any]] = {}
#     for cat, den in cat_den.items():
#         s = (cat_num[cat]/den) if den>0 else 0.0
#         cat_table[cat] = {"score": round(s,2),
#                           "numerator": round(cat_num[cat],2),
#                           "denominator": round(den,2)}

#     return {"mvp_subcategories": sub_table, "mvp_categories": cat_table, "unmapped": unmapped}

# def weighted_final(cat_table: Dict[str,Dict[str,Any]], weights: Dict[str,float]) -> Dict[str,Any]:
#     total = sum(weights.values()) or 1.0
#     final = 0.0; breakdown={}
#     for cat, row in cat_table.items():
#         w = weights.get(cat,0.0)/total
#         s = float(row["score"])
#         final += s*w
#         breakdown[cat] = {"category_score": s, "weight": round(w,4), "weighted": round(s*w,4)}
#     return {"final_score": round(final,2), "breakdown": breakdown}

# def to_csv(path: Path, rows: Dict[str,Dict[str,Any]]):
#     import csv
#     cols = set()
#     for v in rows.values():
#         cols |= set(v.keys())
#     cols = [c for c in sorted(cols) if c!="label"]
#     with path.open("w", newline="", encoding="utf-8") as f:
#         w=csv.writer(f); w.writerow(["label"]+cols)
#         for k,v in rows.items():
#             w.writerow([k]+[v.get(c,"") for c in cols])

# def main():
#     ap = argparse.ArgumentParser(description="Finalize MVP roll-up and weighted final score")
#     ap.add_argument("--aggregate", required=True, help="Path to your aimri_aggregate.json")
#     ap.add_argument("--out", default="aimri_mvp_final.json", help="Output JSON")
#     ap.add_argument("--weights", default="TI=20,DMQ=15,AI=20,BI=15,GOV=10,TS=8,INNO=7,CULT=5",
#                     help="MVP weights as percents, e.g. TI=22,DMQ=13,AI=20,BI=15,GOV=10,TS=8,INNO=7,CULT=5")
#     args = ap.parse_args()

#     agg = load_aggregate(Path(args.aggregate))
#     rolled = rollup(agg)
#     weights = parse_weights(args.weights)
#     final = weighted_final(rolled["mvp_categories"], weights)

#     out = {
#         "meta": agg.get("meta",{}),
#         "mvp_subcategories": rolled["mvp_subcategories"],
#         "mvp_categories": rolled["mvp_categories"],
#         "weights": weights,
#         "aimri_weighted": final,
#         "unmapped_subsections": rolled["unmapped"],  # should be empty if labels match exactly
#     }

#     out_path = Path(args.out)
#     out_path.parent.mkdir(parents=True, exist_ok=True)
#     out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
#     print(f"Wrote {out_path}")


# if __name__ == "__main__":
#     main()
