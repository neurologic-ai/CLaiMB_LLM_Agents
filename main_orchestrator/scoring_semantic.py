# from __future__ import annotations
# from typing import Any, Dict, List, Tuple
# import numpy as np
# from openai import OpenAI

# # ====== Config ======
# OPENAI_MODEL_EMBED = "text-embedding-3-large"

# # ---- AIMRI Framework: 15 Categories with sub-topics ----
# CATEGORIES: Dict[str, Dict[str, List[str]]] = {
#     "01. Technical Infrastructure": {"topics": [
#         "cloud computing capabilities", "computing resources", "development environment",
#         "integration architecture", "security infrastructure"
#     ]},
#     "02. Data Management & Quality": {"topics": [
#         "data architecture", "data quality", "data governance", "data operations", "data accessibility"
#     ]},
#     "03. AI/ML Capabilities": {"topics": [
#         "model development", "production deployment", "mlops maturity",
#         "model governance", "advanced capabilities"
#     ]},
#     "04. Talent & Skills": {"topics": [
#         "technical expertise", "domain knowledge", "team structure",
#         "training and development", "recruitment and retention"
#     ]},
#     "05. Governance & Ethics": {"topics": [
#         "ethical framework", "regulatory compliance", "risk management",
#         "accountability structure", "transparency practices"
#     ]},
#     "06. Strategic Alignment": {"topics": [
#         "business integration", "leadership support", "investment strategy",
#         "innovation management", "partnership ecosystem"
#     ]},
#     "07. Cultural Readiness": {"topics": [
#         "innovation mindset", "change management", "collaboration culture",
#         "decision making", "learning environment"
#     ]},
#     "08. Process Maturity": {"topics": [
#         "project management", "documentation practices", "quality assurance",
#         "operational excellence", "measurement and metrics"
#     ]},
#     "09. Foundation Model Operations": {"topics": [
#         "model integration and deployment", "domain adaptation and fine-tuning",
#         "performance optimization", "risk and compliance management", "scaling and distribution"
#     ]},
#     "10. Generative AI Capabilities": {"topics": [
#         "multi-modal generation", "quality control and validation", "creative workflow integration",
#         "custom generation control", "domain-specific generation"
#     ]},
#     "11. Responsible AI & Social Impact": {"topics": [
#         "algorithmic fairness and bias mitigation", "explainability and interpretability",
#         "privacy and data protection", "ethical impact assessment", "human-AI collaboration"
#     ]},
#     "12. AI Business Value & ROI": {"topics": [
#         "revenue generation and growth", "cost reduction and efficiency",
#         "customer experience enhancement", "innovation and product development",
#         "competitive advantage and market position"
#     ]},
#     "13. AI Risk & Resilience": {"topics": [
#         "data reliability and robustness", "data dependency and vendor lock-in",
#         "vendor and technology risks", "disaster recovery architecture",
#         "regulatory and legal compliance"
#     ]},
#     "14. AI Ecosystem & External Integration": {"topics": [
#         "supplier and vendor AI collaboration", "industry standards and consortiums",
#         "academic and research partnerships", "regulatory and policy engagement"
#     ]},
#     "15. AI Leadership & Vision": {"topics": [
#         "AI strategy and roadmap", "executive AI literacy", "organizational transformation",
#         "future-proofing and adaptability", "thought leadership and industry influence"
#     ]},
# }

# CATEGORY_WEIGHTS = {
#     "01. Technical Infrastructure": 10.0,
#     "02. Data Management & Quality": 5.0,
#     "03. AI/ML Capabilities": 20.0,
#     "04. Talent & Skills": 5.0,
#     "05. Governance & Ethics": 5.0,
#     "06. Strategic Alignment": 5.0,
#     "07. Cultural Readiness": 5.0,
#     "08. Process Maturity": 5.0,
#     "09. Foundation Model Operations": 5.0,
#     "10. Generative AI Capabilities": 5.0,
#     "11. Responsible AI & Social Impact": 5.0,
#     "12. AI Business Value & ROI": 5.0,
#     "13. AI Risk & Resilience": 5.0,
#     "14. AI Ecosystem & External Integration": 5.0,
#     "15. AI Leadership & Vision": 10.0
# }
# SOFTMAX_TEMPERATURE = 0.8
# MIN_WEIGHT_EPS = 0.05


# # ====== Embedding helpers ======
# class EmbeddingClient:
#     def __init__(self, model: str = OPENAI_MODEL_EMBED):
#         self.client = OpenAI()
#         self.model = model

#     def embed(self, texts: List[str]) -> np.ndarray:
#         resp = self.client.embeddings.create(model=self.model, input=texts)
#         vecs = [d.embedding for d in resp.data]
#         return np.array(vecs, dtype=np.float32)

#     @staticmethod
#     def mean_pool(mat: np.ndarray) -> np.ndarray:
#         return mat.mean(axis=0, keepdims=True)

#     @staticmethod
#     def cosine_sim(a: np.ndarray, b: np.ndarray) -> np.ndarray:
#         a = a / np.linalg.norm(a, axis=1, keepdims=True)
#         b = b / np.linalg.norm(b, axis=1, keepdims=True)
#         return a @ b.T


# class SemanticMapper:
#     def __init__(self, embedder: EmbeddingClient):
#         self.embedder = embedder

#     def build_category_vectors(self, categories: Dict[str, Dict]) -> Tuple[List[str], np.ndarray]:
#         names, cat_vecs = [], []
#         for name, meta in categories.items():
#             E = self.embedder.embed(meta["topics"])
#             names.append(name)
#             cat_vecs.append(EmbeddingClient.mean_pool(E)[0])
#         return names, np.vstack(cat_vecs)

#     @staticmethod
#     def softmax(x: np.ndarray, temperature: float = 1.0) -> np.ndarray:
#         x = x / max(temperature, 1e-6)
#         x = x - x.max(axis=1, keepdims=True)
#         e = np.exp(x)
#         return e / e.sum(axis=1, keepdims=True)

#     def map_keys(self, key_texts: Dict[str, str], cat_names: List[str], cat_vecs: np.ndarray) -> Dict[str, Dict[str, float]]:
#         keys = list(key_texts.keys())
#         key_vecs = self.embedder.embed([key_texts[k] for k in keys])
#         sims = EmbeddingClient.cosine_sim(key_vecs, cat_vecs)
#         W = self.softmax(sims, temperature=SOFTMAX_TEMPERATURE)
#         W = np.where(W < MIN_WEIGHT_EPS, 0.0, W)
#         row_sums = W.sum(axis=1, keepdims=True)
#         row_sums[row_sums == 0] = 1.0
#         W = W / row_sums
#         return {keys[i]: {cat_names[j]: float(W[i, j]) for j in range(len(cat_names)) if W[i, j] > 0}
#                 for i in range(len(keys))}


# # ====== Aggregation ======
# class Aggregator:
#     @staticmethod
#     def per_category(aimri_scores: Dict[str, float], key_to_cat: Dict[str, Dict[str, float]]) -> Dict[str, float]:
#         num, den = {}, {}
#         for k, s in aimri_scores.items():
#             for c, w in key_to_cat.get(k, {}).items():
#                 num[c] = num.get(c, 0.0) + s * w
#                 den[c] = den.get(c, 0.0) + w
#         return {c: (num[c] / den[c]) if den[c] > 0 else 0.0 for c in set(num) | set(den)}

#     @staticmethod
#     def weighted_overall(category_scores: Dict[str, float], weights: Dict[str, float]) -> float:
#         return sum(category_scores.get(c, 0.0) * weights.get(c, 0.0) for c in weights.keys())


# # ====== Scoring Agent ======
# class ScoringAgent:
#     def __init__(self, *, category_weights: Dict[str, float] | None = None):
#         self.embedder = EmbeddingClient()
#         self.mapper = SemanticMapper(self.embedder)
#         self.aggregator = Aggregator()
#         self.cat_names, self.cat_vecs = self.mapper.build_category_vectors(CATEGORIES)
#         self.category_weights = category_weights or CATEGORY_WEIGHTS

#     @staticmethod
#     def build_key_texts(scores: Dict[str, float], descriptions: Dict[str, str] | None = None) -> Dict[str, str]:
#         descriptions = descriptions or {}
#         return {k: f"{k}. {descriptions.get(k, '')}".strip() for k in scores.keys()}

#     def run(self, aimri_scores: Dict[str, float], aimri_descriptions: Dict[str, str] | None = None) -> Dict[str, Any]:
#         key_texts = self.build_key_texts(aimri_scores, aimri_descriptions)
#         key_to_cat = self.mapper.map_keys(key_texts, self.cat_names, self.cat_vecs)
#         category_scores = self.aggregator.per_category(aimri_scores, key_to_cat)
#         overall = self.aggregator.weighted_overall(category_scores, self.category_weights)
#         return {
#             "overall_score": overall,
#             "category_scores": category_scores,
#             "key_to_category_weights": key_to_cat,
#             "category_weights_used": self.category_weights,
#         }