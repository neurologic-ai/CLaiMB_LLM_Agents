"""
Recommendation Generator Module (with linear interpolation over recalibrated scores)

Implements mentor steps:
- Contribution fraction per recommendation is based on 1/|affected_categories|, then
  normalized within each category across all recs so the category's fractions sum to 1.
- Expected gain uses TRUE linear interpolation from baseline to recalibrated score:
    expected_gain = (5 - recalibrated_score) * contribution_fraction
  (equivalently: expected_gain_baseline * (5 - recal) / (5 - baseline))
"""

import json
import os
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path
import re
from dotenv import load_dotenv
from collections import defaultdict
try:
    from openai import OpenAI
except ImportError:
    raise ImportError("OpenAI package not installed. Run: pip install openai")

load_dotenv()

class RecommendationGenerator:
    """
    Generate prioritized recommendations from category weights and gap summaries.
    Uses a single LLM call to analyze all categories holistically and then enriches
    each recommendation with quantitative scoring using linear interpolation.
    """

    def __init__(self, api_key: str = None, model: str = "gpt-4-turbo-preview"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key must be provided or set in OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)
        self.model = model

    # --------------------------
    # Loading helpers
    # --------------------------
    # add inside RecommendationGenerator (e.g., right under __init__)
    def _strip_prefix(self, cat_name: str) -> str:
        """Remove numeric prefix like '02. ' or '10. ' from category name."""
        return re.sub(r"^\d{1,2}\.\s*", "", str(cat_name)).strip()
    def load_weights(self, weights_path: str = None) -> Dict[str, float]:
        try:
            from main_orchestrator.scoring import ScoringAgent
            agent = ScoringAgent()
            weights = agent._load_weights()
            if weights:
                print("✓ Loaded category weights from user inputs")
                return weights
        except Exception as e:
            print(f"Could not load weights from ScoringAgent: {e}")

        if weights_path and Path(weights_path).exists():
            try:
                with open(weights_path, 'r') as f:
                    weights = json.load(f)
                print(f"✓ Loaded category weights from {weights_path}")
                return weights
            except Exception as e:
                print(f"Error loading weights from {weights_path}: {e}")

        from main_orchestrator.scoring import CATEGORY_WEIGHTS
        print("⚠️  Using default category weights")
        return CATEGORY_WEIGHTS

    def load_gap_summaries(self, summaries_path: str = None) -> Dict[str, Any]:
        if summaries_path is None:
            workspace_root = Path(__file__).parent.parent
            summaries_path = workspace_root / "results" / "gap_summaries.json"
        with open(summaries_path, 'r') as f:
            data = json.load(f)
        print(f"✓ Loaded gap summaries from {summaries_path}")
        return data

    def load_category_scores(self, scores_path: str = None) -> Dict[str, float]:
        """
        Load baseline category scores from results/category_scores.json
        """
        if scores_path is None:
            scores_path = Path(__file__).parent.parent / "results" / "category_scores.json"
        scores_path = Path(scores_path)
        if not scores_path.exists():
            print(f"⚠️  Baseline scores file not found at {scores_path}; using zeros")
            return {}
        with open(scores_path, "r") as f:
            data = json.load(f)
        return {k: float(v) for k, v in (data or {}).items()}

    def load_recalibrated_scores(self, recal_path: str = None) -> Dict[str, float]:
        """
        Load survey recalibrated category scores (robust path resolver).
        Returns {} when file missing/invalid (caller may fall back to baseline).
        """
        # Candidate file names we’ve seen
        name_candidates = [
            "survey_metric_scores.json",     # current
            "survey_metrics_scores.json",    # plural 'metrics'
            "suervey_metric_scores.json",    # common typo seen earlier
        ]

        # Base dirs to try: explicit env path, then module-root /results, then ORCH.results_root if accessible.
        project_root = Path(__file__).parent.parent.resolve()
        default_env = os.getenv("SURVEY_OUT_SCORES", "./results/survey_metric_scores.json")

        # Build candidate paths in priority order
        candidates: list[Path] = []
        if recal_path:
            candidates.append(Path(recal_path))
        else:
            candidates.append(Path(default_env))

        # If first is relative, also try relative to project root
        try_first = candidates[0]
        if not try_first.is_absolute():
            candidates.append(project_root / try_first)

        # Also try known names under project_root/results
        for nm in name_candidates:
            p = project_root / "results" / nm
            if p not in candidates:
                candidates.append(p)

        # Try ORCH.results_root if available (without importing at module import time)
        try:
            from main_orchestrator.graph_orchestrator import Orchestrator
            orch = Orchestrator(bus_root="./bus", results_root="./results")
            rr = Path(orch.results_root)
            for nm in name_candidates:
                p = rr / nm
                if p not in candidates:
                    candidates.append(p)
        except Exception:
            pass

        chosen: Optional[Path] = None
        for p in candidates:
            if p.exists():
                chosen = p
                break

        if not chosen:
            print("ℹ️ Recalibrated scores not found in any candidate path:")
            for p in candidates:
                print(f"   - {p}")
            print("   Falling back to baseline at runtime.")
            return {}

        # Parse JSON
        try:
            with open(chosen, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"⚠️ Failed to parse recalibrated scores JSON at {chosen}: {e}")
            return {}

        out: Dict[str, float] = {}

        # Preferred shape: {"recalibrated_category_scores": {...}}
        if isinstance(data, dict) and isinstance(data.get("recalibrated_category_scores"), dict):
            out = {k: float(v) for k, v in data["recalibrated_category_scores"].items()}

        # Legacy aggregator shape: {"dimensions": {"<cat>": {"score": x}}}
        elif isinstance(data.get("dimensions"), dict):
            for k, v in data["dimensions"].items():
                try:
                    out[k] = float(v.get("score"))
                except Exception:
                    pass

        # Flat numeric map fallback
        elif isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, (int, float)):
                    out[k] = float(v)

        if out:
            print(f"✓ Loaded recalibrated scores from {chosen} ({len(out)} categories)")
        else:
            print(f"ℹ️ File present but contained no usable recalibrated scores: {chosen}. Falling back to baseline.")

        return out

    # --------------------------
    # Prompting
    # --------------------------
    def generate_consolidated_prompt(self, weights: Dict[str, float],
                                     summaries: Dict[str, Any]) -> str:
        total_weight = sum(weights.values()) or 1.0
        normalized_weights = {k: (v / total_weight * 100) for k, v in weights.items()}

        categories_text = []
        for category, weight_pct in sorted(normalized_weights.items(), key=lambda x: x[1], reverse=True):
            summary_data = summaries.get(category, {})
            score = summary_data.get("score", 0.0)
            recommendation = summary_data.get("recommendation", "No recommendations available.")
            categories_text.append(f"""
### {category}
- **Weight:** {weight_pct:.1f}%
- **Current Score:** {score}/5.0
- **Gap Summary:**
{recommendation}
""")
        categories_section = "\n".join(categories_text)

        prompt = f"""You are an expert AI maturity consultant tasked with generating prioritized recommendations for an organization based on their AI maturity assessment.

                ## Assessment Overview
                You have been provided with 15 categories of AI maturity, each with:
                1. A strategic weight (representing organizational priority)
                2. A current maturity score (0-5 scale)
                3. A detailed gap analysis and recommendations

                ## Category Details (Sorted by Weight)
                {categories_section}

                ## Your Task
                Analyze the above categories holistically and generate **exactly 10 prioritized recommendations** that will have the maximum impact on the organization's AI maturity score and strategic goals.

                ## Prioritization Criteria
                1. **Weight Impact:** Prioritize categories with higher strategic weights
                2. **Score Gap:** Prioritize categories with lower scores (more room for improvement)
                3. **Quick Wins:** Include some achievable recommendations for momentum
                4. **Dependencies:** Consider recommendations that benefit multiple categories
                5. **Strategic Value:** Focus on actions that align with high-weight categories

                ## Output Format (STRICT)
                Return ONLY a valid JSON array with exactly 10 objects. Each object MUST include:
                - "rank": integer 1–10 (1 = highest priority)
                - "title": string
                - "description": string (2–3 sentences)
                - "impact": "High" | "Medium" | "Low"
                - "confidence": number in [0,1]  (probability this rec will measurably improve the affected categories)
                - "affected_categories": array of category strings

                Example element:
                {{
                "rank": 1,
                "title": "Modernize CI/CD for model delivery",
                "description": "……",
                "impact": "High",
                "confidence": 0.83,
                "affected_categories": ["01. Technical Infrastructure", "03. AI/ML Capabilities"]
                }}

                Important:
                - Return ONLY the JSON array. No markdown code fences, no extra commentary.
                - "confidence" must be present for every item and be a float between 0 and 1.

                Generate the recommendations now.
            """
        return prompt

    def call_llm(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system",
                 "content": "You are an expert AI maturity consultant. Always respond with a valid JSON array exactly as specified."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,   # determinism
            max_tokens=3000,
        )
        return response.choices[0].message.content.strip()

    # --------------------------
    # Contribution math
    # --------------------------
    def _raw_shares_per_rec(self, r: Dict[str, Any]) -> Dict[str, float]:
        """
        For a recommendation r, return raw equal shares per affected category: 1/k.
        """
        cats = [c.strip() for c in (r.get("affected_categories") or []) if isinstance(c, str) and c.strip()]
        k = len(cats)
        if k <= 0:
            return {}
        share = 1.0 / float(k)
        return {c: share for c in cats}

    def _normalized_contrib_fractions(
        self, recs: List[Dict[str, Any]]
    ) -> Dict[int, Dict[str, float]]:
        """
        Mentor rule:
          - Within a category c, normalize the per-recommendation raw shares so that
            the contributions across all recs that include c sum to 1.
          - For examples:
              If c appears in three recs with raw shares 1/3, 1/2, 1/2:
                normalized fractions are:
                  r1: (1/3) / (1/3 + 1/2 + 1/2)
                  r2: (1/2) / (1/3 + 1/2 + 1/2)
                  r3: (1/2) / (1/3 + 1/2 + 1/2)
        Returns:
          A dict: rec_index -> {category -> normalized_fraction}.
        """
        # 1) collect raw shares per rec and total per category
        raw_per_rec: List[Dict[str, float]] = []
        cat_totals: Dict[str, float] = defaultdict(float)
        for r in recs:
            shares = self._raw_shares_per_rec(r)
            raw_per_rec.append(shares)
            for c, s in shares.items():
                cat_totals[c] += s

        # 2) normalize within each category
        normalized: Dict[int, Dict[str, float]] = {}
        for idx, shares in enumerate(raw_per_rec):
            out: Dict[str, float] = {}
            for c, s in shares.items():
                denom = cat_totals.get(c, 0.0)
                out[c] = (s / denom) if denom > 0 else 0.0
            normalized[idx] = out
        return normalized

    # --------------------------
    # Linear interpolation enrichment
    # --------------------------
    def _enrich_with_scores(
        self,
        recs: List[Dict[str, Any]],
        baseline_scores: Dict[str, float],
        recal_scores: Dict[str, float],
    ) -> Tuple[List[Dict[str, Any]], Dict[str, float], Dict[str, float]]:
        """
        Linear interpolation of expected gain against recalibrated score:
          expected_gain_baseline = (5 - baseline) * frac
          expected_gain_recal    = expected_gain_baseline * ((5 - recal) / (5 - baseline))
                                 = (5 - recal) * frac
        new_estimated_score = min(5, baseline + expected_gain_recal)

        Returns:
          - enriched recs
          - category_sums: total normalized contribution per category (always 1.0 if category appears)
          - category_projection: aggregate expected_gain per category and projected new score
        """
        MAX_SCORE = 5.0

        # Compute normalized fractions per rec/category
        norm_fracs = self._normalized_contrib_fractions(recs)

        # For meta: how much each category sums to (should be 1.0 if it appears)
        cat_sum_norm: Dict[str, float] = defaultdict(float)
        for idx in range(len(recs)):
            for c, f in (norm_fracs.get(idx) or {}).items():
                cat_sum_norm[c] += f

        # Attach per-recommendation score details
        for idx, r in enumerate(recs):
            cats = r.get("affected_categories") or []
            details_out = {}
            for cat in cats:
                if not isinstance(cat, str) or not cat.strip():
                    continue
                c = cat.strip()

                base = float(baseline_scores.get(c, 0.0))
                recal = float(recal_scores.get(c, base))
                gap_base = max(0.0, MAX_SCORE - base)
                gap_recal = max(0.0, MAX_SCORE - recal)
                frac = float((norm_fracs.get(idx) or {}).get(c, 0.0))

                # Linear interpolation result
                scale = (gap_recal / gap_base) if gap_base > 0 else 0.0
                expected_gain = gap_recal * frac
                new_score = min(MAX_SCORE, recal + expected_gain)

                # Use stripped category name in output
                pretty = self._strip_prefix(c)
                details_out[pretty] = {
                    # "contribution_fraction": round(frac, 4),
                    # "expected_gain": round(expected_gain, 3),
                    "Recommendable_Score": round(new_score, 3),
                    # "baseline_score": round(base, 2),
                    "Current_Score": round(recal, 3),
                    # "gap_base": round(gap_base, 2),
                    # "gap_recal": round(gap_recal, 2),
                    # "linear_scale": round(scale, 4),
                }

            # Replace categories with stripped ones for output
            r["affected_categories"] = [
                self._strip_prefix(c) for c in cats if isinstance(c, str) and c.strip()
            ]
            r["score_details"] = details_out

        # Build category projection totals (unchanged internally)
        proj_gain: Dict[str, float] = defaultdict(float)
        for r in recs:
            for c, d in (r.get("score_details") or {}).items():
                proj_gain[c] += float(d.get("expected_gain", 0.0))

        category_projection: Dict[str, Dict[str, float]] = {}
        for c, base in baseline_scores.items():
            tgain = proj_gain.get(self._strip_prefix(c), 0.0)
            category_projection[self._strip_prefix(c)] = {
                "baseline_score": round(float(base), 2),
                "total_expected_gain": round(tgain, 2),
                "projected_new_score": round(min(MAX_SCORE, float(base) + tgain), 2),
            }

        # Also clean up meta keys for consistency
        cat_sum_norm = {self._strip_prefix(k): round(v, 4) for k, v in cat_sum_norm.items()}

        return recs, cat_sum_norm, category_projection

    # --------------------------
    # Public API
    # --------------------------
    def generate_recommendations(
        self,
        weights_path: str = None,
        summaries_path: str = None,
        save_output: bool = True,
        output_path: str = None
    ) -> Dict[str, Any]:

        print("\n" + "=" * 80)
        print("RECOMMENDATION GENERATOR - Holistic Priority Analysis (linear interpolation)")
        print("=" * 80 + "\n")

        # Inputs
        print("Loading category weights...")
        _ = self.load_weights(weights_path)  # weights not used in scoring math here; kept for future

        print("Loading gap summaries...")
        summaries = self.load_gap_summaries(summaries_path)

        print("Loading baseline category scores...")
        baseline_scores = self.load_category_scores()

        print("Loading recalibrated (survey) scores...")
        recal_scores = self.load_recalibrated_scores()

        # Prompt & call LLM
        print("\n🤖 Generating consolidated prompt...")
        prompt = self.generate_consolidated_prompt(_, summaries)
        print(f"📡 Calling LLM ({self.model})...")
        raw = self.call_llm(prompt)

        # Parse JSON
        try:
            recs = json.loads(raw)
            if not isinstance(recs, list) or len(recs) != 10:
                raise ValueError("LLM did not return exactly 10 recommendations.")
        except Exception:
            print("❌ Failed to parse LLM response as JSON array of 10 items.")
            print(raw[:800])
            raise

        # Enrich with linear interpolation scoring
        enriched, cat_norm_sums, category_projection = self._enrich_with_scores(
            recs, baseline_scores, recal_scores
        )

        result = {
            "Overall Prioritized Recommendations": {
                "recommendation":
                    f"Generated {len(enriched)} prioritized recommendations with linear interpolation scoring.",
                "prioritized_actions": enriched
            },
            # "scoring_meta": {
            #     "baseline_category_scores": baseline_scores,
            #     "recalibrated_category_scores": recal_scores or baseline_scores,
            #     "normalized_contribution_sums_per_category": cat_norm_sums,
            #     "category_projection": category_projection
            # }
        }

        # Save
        if save_output:
            if output_path is None:
                output_path = Path(__file__).parent.parent / "results" / "prioritized_recommendations.json"
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                json.dump(result, f, indent=2)
            print(f"\n✅ Recommendations saved to: {output_path}")

        # Summary print
        self._print_summary(result)
        return result

    def _print_summary(self, result: Dict[str, Any]):
        print("\n" + "=" * 80)
        print("📋 RECOMMENDATION SUMMARY (linear interpolation)")
        print("=" * 80)
        overall = result.get("Overall Prioritized Recommendations", {})
        recs = overall.get("prioritized_actions", [])
        print(f"\nTotal Recommendations: {len(recs)}")
        hi = sum(1 for r in recs if str(r.get("impact", "")).lower() == "high")
        print(f"High Impact Recommendations: {hi}")

        for r in sorted(recs, key=lambda x: x.get("rank", 999))[:3]:
            print(f"\n  {r.get('rank')}. {r.get('title')}")
            print(f"     Impact: {r.get('impact')} | Confidence: {r.get('confidence')}")
            cats = list((r.get("affected_categories") or [])[:3])
            print(f"     Affects: {', '.join(cats)}")
        print("\n" + "=" * 80)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate prioritized recommendations with linear interpolation")
    parser.add_argument("--api-key", help="OpenAI API key (or set OPENAI_API_KEY)")
    parser.add_argument("--model", default="gpt-4-turbo-preview", help="LLM model to use")
    parser.add_argument("--weights", help="Path to category weights JSON file")
    parser.add_argument("--summaries", help="Path to gap summaries JSON file")
    parser.add_argument("--no-save", action="store_true", help="Don't save output to file")
    args = parser.parse_args()

    try:
        generator = RecommendationGenerator(api_key=args.api_key, model=args.model)
        generator.generate_recommendations(
            weights_path=args.weights,
            summaries_path=args.summaries,
            save_output=not args.no_save
        )
        print("\n✅ Recommendation generation complete!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()