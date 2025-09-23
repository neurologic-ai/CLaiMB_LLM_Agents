#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
import yaml
from main_orchestrator.scoring import CATEGORIES as AIMRI_CATEGORIES
from main_orchestrator.scoring import CATEGORY_WEIGHTS

# -----------------------------
# Config
# -----------------------------
OPENAI_MODEL_EMBED = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")

# -----------------------------
# Embedding helper
# -----------------------------
class EmbeddingClient:
    def __init__(self, model: str = OPENAI_MODEL_EMBED):
        load_dotenv()
        self.client = OpenAI()
        self.model = model

    def embed(self, texts: List[str]) -> np.ndarray:
        if not texts:
            # dim 1536 for t-e-3-small; adjust if you switch models
            return np.zeros((0, 1536), dtype=np.float32)
        resp = self.client.embeddings.create(model=self.model, input=texts)
        vecs = [d.embedding for d in resp.data]
        return np.array(vecs, dtype=np.float32)

    @staticmethod
    def cosine_sim(a: np.ndarray, b: np.ndarray) -> np.ndarray:
        a = a / (np.linalg.norm(a, axis=1, keepdims=True) + 1e-9)
        b = b / (np.linalg.norm(b, axis=1, keepdims=True) + 1e-9)
        return a @ b.T


# -----------------------------
# Survey loader (YAML or CSV)
# -----------------------------
def load_survey(path_like: Path | str) -> Tuple[List[str], List[Any]]:
    """
    Loads survey items from:
      - YAML: list of {id, question, [score]?}. If score missing -> random 1..5
      - CSV: messy Excel-CSV; finds header row containing both 'Questions' and 'Score'
    Returns (questions_text_list, responses_list)
    """
    p = Path(path_like)
    suffix = p.suffix.lower()

    # YAML branch
    if suffix in {".yaml", ".yml"}:
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError("YAML survey must be a list of {id, question, [score]} objects.")
        questions: List[str] = []
        responses: List[Any] = []
        import random
        for item in data:
            if not isinstance(item, dict):
                continue
            qid = item.get("id")
            qtext = item.get("question")
            if not qid or not qtext:
                continue
            score = item.get("score")
            if score is None:
                score = random.randint(1, 5)
            questions.append(f"{qid}: {qtext}")
            responses.append(score)
        if not questions:
            raise ValueError("No valid questions found in YAML survey.")
        return questions, responses

    # CSV branch (robust to header noise)
    raw = pd.read_csv(p, header=None, dtype=str, keep_default_na=False)
    norm = raw.apply(lambda col: col.astype(str).str.strip().str.lower())

    def is_header_row(row) -> bool:
        vals = set(row.tolist())
        return ("questions" in vals) and ("score" in vals)

    header_mask = norm.apply(is_header_row, axis=1)
    if not header_mask.any():
        raise ValueError(
            "Couldn't find a header row containing both 'Questions' and 'Score' in the CSV."
        )
    hdr_idx = header_mask.idxmax()
    header = raw.iloc[hdr_idx].tolist()
    df = raw.iloc[hdr_idx + 1 :].copy()
    df.columns = header

    # Clean empties
    df = df.dropna(axis=1, how="all")
    df = df.replace({"": None}).dropna(how="all")

    # Map columns case-insensitively
    col_map = {str(c).strip().lower(): c for c in df.columns if isinstance(c, str)}
    q_col = col_map.get("questions")
    s_col = col_map.get("score")
    r_col = col_map.get("response")  # optional

    if not q_col or not s_col:
        raise ValueError(f"Expected columns 'Questions' and 'Score'. Found: {df.columns.tolist()}")

    questions: List[str] = []
    responses: List[Any] = []
    for _, row in df.iterrows():
        q = str(row.get(q_col, "")).strip()
        s_raw = row.get(s_col, None)
        r = str(row.get(r_col, "")).strip() if r_col in df.columns else ""
        if not q or s_raw in (None, ""):
            continue
        # keep response as-is (string), we’ll parse later
        txt = f"{q} — {r}" if r else q
        questions.append(txt)
        responses.append(s_raw)

    if not questions:
        raise ValueError("No usable rows found under detected CSV header.")
    return questions, responses


# -----------------------------
# YAML metric descriptions loader (optional)
# -----------------------------
def load_metric_texts(yaml_paths: List[Path]) -> List[str]:
    texts: List[str] = []
    for yp in yaml_paths:
        try:
            obj = yaml.safe_load(Path(yp).read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(obj, dict) and isinstance(obj.get("metrics"), list):
            for m in obj["metrics"]:
                desc = (m or {}).get("description")
                if isinstance(desc, str) and desc.strip():
                    texts.append(desc.strip())
    return texts


# -----------------------------
# Response → numeric score
# -----------------------------
LIKERT_MAP = {
    r"^strongly\s*disagree$": 1,
    r"^disagree$": 2,
    r"^neutral$": 3,
    r"^agree$": 4,
    r"^strongly\s*agree$": 5,
}

def parse_response_to_score(resp: str) -> Optional[float]:

    s = (resp or "").strip()
    if not s:
        return None
    try:
        val = float(s)
        if 0 <= val <= 5:
            return val
    except Exception:
        pass

    low = s.lower().strip()
    for pat, v in LIKERT_MAP.items():
        if re.search(pat, low):
            return float(v)

    m = re.search(r"([0-5])(?:\D*)$", s)
    if m:
        try:
            return float(m.group(1))
        except Exception:
            pass

    nums = re.findall(r"\d+(?:\.\d+)?", s)
    if nums:
        try:
            val = float(nums[-1])
            if 0 <= val <= 5:
                return val
        except Exception:
            pass

    return None


# -----------------------------
# Category mapping via embeddings
# -----------------------------
def build_category_corpus() -> Tuple[List[str], List[str]]:
    names, texts = [], []
    for name, meta in AIMRI_CATEGORIES.items():
        topics = meta.get("topics", [])
        txt = f"{name}. " + "; ".join(topics)
        names.append(name)
        texts.append(txt)
    return names, texts


def map_questions_to_categories(
    questions: List[str],
    embedder: EmbeddingClient,
    extra_texts: Optional[List[str]] = None,
) -> Tuple[List[str], List[float], Dict[int, Dict[str, Any]]]:
    cat_names, cat_texts = build_category_corpus()
    E_cat = embedder.embed(cat_texts)
    E_q = embedder.embed(questions)
    S = EmbeddingClient.cosine_sim(E_q, E_cat)

    blend_alpha = 0.15  # small bonus for nearby metric-text similarity
    if extra_texts:
        E_extra = embedder.embed(extra_texts)
        S_extra = EmbeddingClient.cosine_sim(E_q, E_extra).max(axis=1)
        S = S + blend_alpha * S_extra[:, None]

    best_idx = S.argmax(axis=1)
    best_sim = S.max(axis=1)

    best_names = [cat_names[i] for i in best_idx]
    audit: Dict[int, Dict[str, Any]] = {}
    for i, q in enumerate(questions):
        row = S[i]
        topk = np.argsort(-row)[:5]
        audit[i] = {
            "question": q,
            "best_category": cat_names[best_idx[i]],
            "similarity": float(best_sim[i]),
            "alternatives": [
                {"category": cat_names[j], "sim": float(row[j])} for j in topk
            ],
        }
    return best_names, best_sim.tolist(), audit


# -----------------------------
# Recalibration math
# -----------------------------
def weighted_overall(category_scores: Dict[str, float], weights: Dict[str, float]) -> float:
    total_w = sum(weights.values()) or 1.0
    return sum(category_scores.get(k, 0.0) * (weights[k] / total_w) for k in weights)


def recalibrate_scores(
    existing_category_scores: Dict[str, float],
    existing_category_N: Dict[str, int],
    survey_contribs: Dict[str, List[float]],
) -> Tuple[Dict[str, float], Dict[str, Any]]:
    out: Dict[str, float] = {}
    audit: Dict[str, Any] = {}
    cats = set(list(existing_category_scores.keys()) + list(survey_contribs.keys()))
    for c in sorted(cats):
        old = float(existing_category_scores.get(c, 0.0))
        N = int(existing_category_N.get(c, 1))
        sv = survey_contribs.get(c, [])
        M = len(sv)
        new = old if (N + M) == 0 else (old * N + sum(sv)) / (N + M)
        out[c] = round(new, 2)
        audit[c] = {
            "existing_score": round(old, 2),
            "N": N,
            "survey_scores": [float(x) for x in sv],
            "M": M,
            "new_score": round(new, 2),
        }
    return out, audit


# -----------------------------
# Main CLI
# -----------------------------
@dataclass
class Args:
    survey: Path
    yamls: List[Path]
    out_scores: Path
    out_audit: Path
    existing_json: Optional[Path]
    default_N: int


def load_existing(existing_json: Optional[Path], default_N: int) -> Tuple[Dict[str, float], Dict[str, int]]:
    """
    Supports two formats:

    A) Old aggregator:
       { "dimensions": { "<cat>": {"score": X, "metric_contributions": N}, ... } }

    B) Flat map (your file):
       { "<cat>": X, ... } OR { "<cat>": {"score": X}, ... }

    Any categories missing in the file will keep the defaults:
      score = 0.0  (or change to a baseline if you prefer)
      N = default_N
    """
    scores: Dict[str, float] = {k: 0.0 for k in AIMRI_CATEGORIES.keys()}
    Ns: Dict[str, int] = {k: default_N for k in AIMRI_CATEGORIES.keys()}

    if not existing_json:
        return scores, Ns

    try:
        obj = json.loads(Path(existing_json).read_text())
    except Exception:
        return scores, Ns

    if not isinstance(obj, dict):
        return scores, Ns

    # Format A: old aggregator
    if isinstance(obj.get("dimensions"), dict):
        for k, v in obj["dimensions"].items():
            if k in scores and isinstance(v, dict):
                if "score" in v:
                    try:
                        scores[k] = float(v["score"])
                    except Exception:
                        pass
                if "metric_contributions" in v:
                    try:
                        Ns[k] = max(int(v["metric_contributions"]), 1)
                    except Exception:
                        pass
        return scores, Ns

    # Format B: flat map
    for k, v in obj.items():
        if k not in scores:
            continue
        try:
            if isinstance(v, dict) and "score" in v:
                scores[k] = float(v["score"])
            elif isinstance(v, (int, float)):
                scores[k] = float(v)
            elif isinstance(v, str):
                scores[k] = float(v)
        except Exception:
            pass

    return scores, Ns

def main_with_args(args: Args):
    questions, responses = load_survey(args.survey)
    parsed_scores = []
    for r in responses:
        if isinstance(r, (int, float)):
            s = float(r)
            parsed_scores.append(s if 0 <= s <= 5 else None)
        else:
            parsed_scores.append(parse_response_to_score(str(r)))
    qrs = [(q, s) for q, s in zip(questions, parsed_scores) if s is not None]
    if not qrs:
        raise ValueError("No survey rows produced a numeric score in [0..5].")
    extra_texts = load_metric_texts(args.yamls) if args.yamls else []
    embedder = EmbeddingClient()
    best_categories, sims, mapping_audit = map_questions_to_categories(
        [q for q, _ in qrs], embedder, extra_texts=extra_texts
    )
    survey_contribs = {k: [] for k in AIMRI_CATEGORIES.keys()}
    for (_, score), cat in zip(qrs, best_categories):
        survey_contribs[cat].append(float(score))
    existing_scores, existing_N = load_existing(args.existing_json, args.default_N)
    recalib_scores, per_cat_audit = recalibrate_scores(existing_scores, existing_N, survey_contribs)
    overall = round(weighted_overall(recalib_scores, CATEGORY_WEIGHTS), 2)
    args.out_scores.parent.mkdir(parents=True, exist_ok=True)
    args.out_audit.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out_scores, "w", encoding="utf-8") as f:
        json.dump({"recalibrated_category_scores": recalib_scores,
                   "overall_weighted": overall,
                   "weights_used": CATEGORY_WEIGHTS}, f, indent=2)
    with open(args.out_audit, "w", encoding="utf-8") as f:
        json.dump({"survey_rows_used": len(qrs),
                   "survey_total_rows": len(questions),
                   "mapping_audit": mapping_audit,
                   "per_category": per_cat_audit,
                   "existing_source": str(args.existing_json) if args.existing_json else None}, f, indent=2)
    return recalib_scores

def main():
    ap = argparse.ArgumentParser(description="Recalibrate AIMRI category scores with survey responses.")
    ap.add_argument("--survey", required=True, type=Path, help="Path to survey YAML or CSV.")
    ap.add_argument("--yaml", nargs="*", default=[], type=Path, help="Optional metric-description YAMLs.")
    ap.add_argument("--existing-json", type=Path, default=None,
                    help="Optional existing aggregated JSON (old aggregator output with 'dimensions').")
    ap.add_argument("--out-scores", required=True, type=Path, help="Output JSON path for recalibrated scores.")
    ap.add_argument("--out-audit", required=True, type=Path, help="Output JSON path for audit trail.")
    ap.add_argument("--default-N", type=int, default=5,
                    help="Fallback N when existing aggregator does not provide contributions (default: 5).")
    args_ns = ap.parse_args()

    args = Args(
        survey=args_ns.survey,
        yamls=args_ns.yaml or [],
        out_scores=args_ns.out_scores,
        out_audit=args_ns.out_audit,
        existing_json=args_ns.existing_json,
        default_N=args_ns.default_N,
    )

    # 1) Load survey (YAML or CSV)
    questions, responses = load_survey(args.survey)

    # 2) Parse response → numeric score
    parsed_scores: List[Optional[float]] = []
    for r in responses:
        if isinstance(r, (int, float)):
            s = float(r)
            if 0 <= s <= 5:
                parsed_scores.append(s)
            else:
                parsed_scores.append(None)
        else:
            parsed_scores.append(parse_response_to_score(str(r)))

    qrs = [(q, s) for q, s in zip(questions, parsed_scores) if s is not None]
    if not qrs:
        raise ValueError("No survey rows produced a numeric score in [0..5].")

    # 3) Load optional YAML metric descriptions (extra semantic context)
    extra_texts: List[str] = load_metric_texts(args.yamls) if args.yamls else []

    # 4) Map questions → AIMRI category
    embedder = EmbeddingClient()
    best_categories, sims, mapping_audit = map_questions_to_categories(
        [q for q, _ in qrs], embedder, extra_texts=extra_texts
    )

    # 5) Collect survey contributions per category
    survey_contribs: Dict[str, List[float]] = {k: [] for k in AIMRI_CATEGORIES.keys()}
    for (_, score), cat in zip(qrs, best_categories):
        survey_contribs[cat].append(float(score))

    # 6) Load existing category scores + N (from old aggregator JSON if provided)
    existing_scores, existing_N = load_existing(args.existing_json, args.default_N)

    # 7) Recalibrate
    recalib_scores, per_cat_audit = recalibrate_scores(existing_scores, existing_N, survey_contribs)

    # 8) Overall (weighted)
    overall = round(weighted_overall(recalib_scores, CATEGORY_WEIGHTS), 2)

    # 9) Save outputs
    args.out_scores.parent.mkdir(parents=True, exist_ok=True)
    args.out_audit.parent.mkdir(parents=True, exist_ok=True)

    with open(args.out_scores, "w", encoding="utf-8") as f:
        json.dump(
            {
                "recalibrated_category_scores": recalib_scores,
                "overall_weighted": overall,
                "weights_used": CATEGORY_WEIGHTS,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    with open(args.out_audit, "w", encoding="utf-8") as f:
        json.dump(
            {
                "survey_rows_used": len(qrs),
                "survey_total_rows": len(questions),
                "mapping_audit": mapping_audit,
                "per_category": per_cat_audit,
                "existing_source": str(args.existing_json) if args.existing_json else None,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    print(f"Wrote {args.out_scores}")
    print(f"Wrote {args.out_audit}")


if __name__ == "__main__":
    main()