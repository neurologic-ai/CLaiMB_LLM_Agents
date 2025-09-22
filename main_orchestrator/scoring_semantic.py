from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from openai import OpenAI

# ====== Config ======
OPENAI_MODEL_EMBED = "text-embedding-3-large"

CATEGORY_WEIGHTS = {
    "Technical Infrastructure": 0.20,
    "Data Management & Quality": 0.15,
    "AI/ML Capabilities": 0.20,
    "Business Integration": 0.15,
    "Governance & Risk Management": 0.10,
    "Talent & Skills": 0.08,
    "Innovation & Research": 0.07,
    "Cultural Readiness": 0.05,
}

SOFTMAX_TEMPERATURE = 0.8
MIN_WEIGHT_EPS = 0.05

CATEGORIES = {
    "Technical Infrastructure": {"topics": [
        "cloud infrastructure","compute resources","networking","storage",
        "kubernetes","autoscaling","infrastructure as code","ci cd",
        "developer environment","observability"
    ]},
    "Data Management & Quality": {"topics": [
        "data architecture","data quality","data governance","metadata",
        "lineage","freshness","validation","stewardship"
    ]},
    "AI/ML Capabilities": {"topics": [
        "model development","ml experimentation","mlops maturity","model registry",
        "production deployment","monitoring","drift detection","feature store"
    ]},
    "Business Integration": {"topics": [
        "use case implementation","strategic alignment","roi measurement",
        "decision traceability","bi adoption","self service analytics"
    ]},
    "Governance & Risk Management": {"topics": [
        "regulatory compliance","ethical ai","risk management","security posture",
        "pii controls","policy enforcement"
    ]},
    "Talent & Skills": {"topics": [
        "technical expertise","domain knowledge","team structure",
        "upskilling","training programs"
    ]},
    "Innovation & Research": {"topics": [
        "innovation pipeline","r and d investment","experimentation rate",
        "external partnerships","proof of concept"
    ]},
    "Cultural Readiness": {"topics": [
        "change management","collaboration culture","learning environment",
        "data driven culture","adoption"
    ]}
}

class EmbeddingClient:
    def __init__(self, model: str = OPENAI_MODEL_EMBED):
        self.client = OpenAI()
        self.model = model

    def embed(self, texts: List[str]) -> np.ndarray:
        resp = self.client.embeddings.create(model=self.model, input=texts)
        vecs = [d.embedding for d in resp.data]
        return np.array(vecs, dtype=np.float32)

    @staticmethod
    def mean_pool(mat: np.ndarray) -> np.ndarray:
        return mat.mean(axis=0, keepdims=True)

    @staticmethod
    def cosine_sim(a: np.ndarray, b: np.ndarray) -> np.ndarray:
        a = a / np.linalg.norm(a, axis=1, keepdims=True)
        b = b / np.linalg.norm(b, axis=1, keepdims=True)
        return a @ b.T

class SemanticMapper:
    def __init__(self, embedder: EmbeddingClient):
        self.embedder = embedder

    def build_category_vectors(self, categories: Dict[str, Dict]) -> Tuple[List[str], np.ndarray]:
        names, cat_vecs = [], []
        for name, meta in categories.items():
            E = self.embedder.embed(meta["topics"])
            names.append(name)
            cat_vecs.append(EmbeddingClient.mean_pool(E)[0])
        return names, np.vstack(cat_vecs)

    @staticmethod
    def softmax(x: np.ndarray, temperature: float = 1.0) -> np.ndarray:
        x = x / max(temperature, 1e-6)
        x = x - x.max(axis=1, keepdims=True)
        e = np.exp(x)
        return e / e.sum(axis=1, keepdims=True)

    def map_keys(self, key_texts: Dict[str, str], cat_names: List[str], cat_vecs: np.ndarray) -> Dict[str, Dict[str, float]]:
        keys = list(key_texts.keys())
        key_vecs = self.embedder.embed([key_texts[k] for k in keys])
        sims = EmbeddingClient.cosine_sim(key_vecs, cat_vecs)
        W = self.softmax(sims, temperature=SOFTMAX_TEMPERATURE)
        W = np.where(W < MIN_WEIGHT_EPS, 0.0, W)
        row_sums = W.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1.0
        W = W / row_sums
        return {keys[i]: {cat_names[j]: float(W[i, j]) for j in range(len(cat_names)) if W[i, j] > 0}
                for i in range(len(keys))}

class Aggregator:
    @staticmethod
    def per_category(aimri_scores: Dict[str, float], key_to_cat: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        num, den = {}, {}
        for k, s in aimri_scores.items():
            for c, w in key_to_cat.get(k, {}).items():
                num[c] = num.get(c, 0.0) + s * w
                den[c] = den.get(c, 0.0) + w
        return {c: (num[c] / den[c]) if den[c] > 0 else 0.0 for c in set(num) | set(den)}

    @staticmethod
    def weighted_overall(category_scores: Dict[str, float], weights: Dict[str, float]) -> float:
        return sum(category_scores.get(c, 0.0) * w for c, w in weights.items())

class ScoringAgent:
    def __init__(self):
        self.embedder = EmbeddingClient()
        self.mapper = SemanticMapper(self.embedder)
        self.aggregator = Aggregator()
        self.cat_names, self.cat_vecs = self.mapper.build_category_vectors(CATEGORIES)

    @staticmethod
    def build_key_texts(scores: Dict[str, float], descriptions: Dict[str, str] | None = None) -> Dict[str, str]:
        descriptions = descriptions or {}
        return {k: f"{k}. {descriptions.get(k, '')}".strip() for k in scores.keys()}

    def run(self, aimri_scores: Dict[str, float], aimri_descriptions: Dict[str, str] | None = None) -> Dict[str, Any]:
        key_texts = self.build_key_texts(aimri_scores, aimri_descriptions)
        key_to_cat = self.mapper.map_keys(key_texts, self.cat_names, self.cat_vecs)
        category_scores = self.aggregator.per_category(aimri_scores, key_to_cat)
        overall = self.aggregator.weighted_overall(category_scores, CATEGORY_WEIGHTS)
        return {
            "overall_score": overall,
            "category_scores": category_scores,
            "key_to_category_weights": key_to_cat,
            "category_weights_used": CATEGORY_WEIGHTS,
        }