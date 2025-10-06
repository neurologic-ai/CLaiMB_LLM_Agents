# from __future__ import annotations
# from typing import Any, Dict, List, Optional
# import re
# from loguru import logger

# from data_collection_agents.dev_env_scanner_agent.base_agent import BaseMicroAgent
# from data_collection_agents.dev_env_scanner_agent.one_shot.registry import get_one_shot
# from data_collection_agents.dev_env_scanner_agent.one_shot.prompting import build_metric_prompt
# from data_collection_agents.dev_env_scanner_agent.logging_utils import timed

# _MAX_SNIPPETS = 12
# _MAX_SNIPPET_CHARS = 1800
# _JSON_ONLY_SYSTEM = (
#     "You are a strict grader. Return ONLY a single JSON object with the exact keys shown in the example. "
#     "Do not include markdown, backticks, or extra text."
# )

# def _shrink_text(text: str, limit: int) -> str:
#     if len(text) <= limit:
#         return text
#     text = re.sub(r'\"\"\"[\\s\\S]*?\"\"\"', '\"\"\"…\"\"\"', text)
#     text = re.sub(r"'''[\\s\\S]*?'''", "'''…'''", text)
#     if len(text) <= limit:
#         return text
#     out, total = [], 0
#     for line in text.splitlines():
#         n = len(line) + 1
#         if total + n > limit:
#             break
#         out.append(line)
#         total += n
#     return "\n".join(out)

# def _compact_snippets(snippets: List[str]) -> List[str]:
#     out: List[str] = []
#     for s in (snippets or [])[:_MAX_SNIPPETS]:
#         s = _shrink_text(s or "", _MAX_SNIPPET_CHARS)
#         if s.strip():
#             out.append(s)
#     return out

# def _normalize_band(val: Any, default: int = 3) -> int:
#     try:
#         v = int(val)
#         return 1 if v < 1 else 5 if v > 5 else v
#     except Exception:
#         return default

# def _finalize_metric(out: Dict[str, Any], metric_id: str) -> Dict[str, Any]:
#     out = dict(out or {})
#     out.setdefault("metric_id", metric_id)
#     out["band"] = _normalize_band(out.get("band", 3))
#     out.setdefault("rationale", "No rationale.")
#     out.setdefault("flags", [])
#     out.setdefault("gaps", [])
#     return out

# def _call_llm_json(agent: BaseMicroAgent, prompt: str, system_prompt: str = _JSON_ONLY_SYSTEM) -> Dict[str, Any]:
#     raw = agent._call_llm(prompt, system_prompt=system_prompt)
#     parsed = agent._parse_json_response(raw)
#     if isinstance(parsed, dict):
#         return parsed
#     try:
#         raw2 = agent._call_llm(prompt, system_prompt=system_prompt, temperature=0)
#         parsed2 = agent._parse_json_response(raw2)
#         if isinstance(parsed2, dict):
#             return parsed2
#     except Exception:
#         pass
#     return {}

# class CyclomaticComplexityAgent(BaseMicroAgent):
#     METRIC_ID = "code.cyclomatic_complexity_band"
#     RUBRIC = (
#         "Use avg_complexity and distribution across low/med/high/very_high.\n"
#         "Band 5: avg ≤ 5 and ≤10% functions high/very_high;\n"
#         "Band 4: avg ≤ 7 and ≤20% high/very_high;\n"
#         "Band 3: avg ≤ 10 or 21–35% high/very_high;\n"
#         "Band 2: avg ≤ 12 or 36–50% high/very_high;\n"
#         "Band 1: avg > 12 or widespread very_high complexity or evidence missing."
#     )
#     INPUT_MEANINGS = {"code_snippets[]": "Representative source slices to infer complexity distribution."}

#     def evaluate(self, code_snippets: List[str], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
#         ex = get_one_shot(self.__class__.__name__)
#         compact = _compact_snippets(code_snippets)
#         task_input = {"code_snippets": compact}
#         prompt = build_metric_prompt(
#             rubric=self.RUBRIC, metric_id=self.METRIC_ID,
#             input_key_meanings=self.INPUT_MEANINGS, task_input=task_input,
#             example_input=ex["example_input"], example_output=ex["example_output"],
#         )
#         logger.debug(f"[{self.METRIC_ID}] prompt_len={len(prompt)}; n_snippets={len(compact)}")
#         with timed(f"metric.{self.METRIC_ID}"):
#             out = _call_llm_json(self, prompt)
#         out = _finalize_metric(out, self.METRIC_ID)
#         logger.info(f"[{self.METRIC_ID}] band={out['band']} rationale={out['rationale']}")
#         if out["flags"]: logger.info(f"[{self.METRIC_ID}] flags={out['flags']}")
#         if out["gaps"]:  logger.info(f"[{self.METRIC_ID}] gaps={out['gaps']}")
#         return out

# class DocstringCoverageAgent(BaseMicroAgent):
#     METRIC_ID = "code.docstring_coverage_band"
#     RUBRIC = (
#         "Use coverage and quality together.\n"
#         "Band 5: coverage ≥0.90 and quality ≥0.85;\n"
#         "Band 4: coverage ≥0.80 and quality ≥0.75;\n"
#         "Band 3: coverage ≥0.65 and quality ≥0.60;\n"
#         "Band 2: coverage ≥0.45 or quality ≥0.45;\n"
#         "Band 1: below the above or major gaps."
#     )
#     INPUT_MEANINGS = {"code_snippets[]": "Slices showing functions/classes to infer docstring density & quality."}

#     def evaluate(self, code_snippets: List[str], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
#         ex = get_one_shot(self.__class__.__name__)
#         compact = _compact_snippets(code_snippets)
#         task_input = {"code_snippets": compact}
#         prompt = build_metric_prompt(
#             rubric=self.RUBRIC, metric_id=self.METRIC_ID,
#             input_key_meanings=self.INPUT_MEANINGS, task_input=task_input,
#             example_input=ex["example_input"], example_output=ex["example_output"],
#         )
#         logger.debug(f"[{self.METRIC_ID}] prompt_len={len(prompt)}; n_snippets={len(compact)}")
#         with timed(f"metric.{self.METRIC_ID}"):
#             out = _call_llm_json(self, prompt)
#         out = _finalize_metric(out, self.METRIC_ID)
#         logger.info(f"[{self.METRIC_ID}] band={out['band']} rationale={out['rationale']}")
#         if out["flags"]: logger.info(f"[{self.METRIC_ID}] flags={out['flags']}")
#         if out["gaps"]:  logger.info(f"[{self.METRIC_ID}] gaps={out['gaps']}")
#         return out

# class MaintainabilityAgent(BaseMicroAgent):
#     METRIC_ID = "code.maintainability_band"
#     RUBRIC = (
#         "Use maintainability/readability/design as joint evidence.\n"
#         "Band 5: all ≥0.85 and consistent across files;\n"
#         "Band 4: all ≥0.75 or two ≥0.80;\n"
#         "Band 3: all ≥0.60 with mixed signals;\n"
#         "Band 2: any <0.60 but some strengths present;\n"
#         "Band 1: multiple <0.50 or major smells dominate."
#     )
#     INPUT_MEANINGS = {"code_snippets[]": "Representative code spanning classes, functions, and branching."}

#     def evaluate(self, code_snippets: List[str], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
#         ex = get_one_shot(self.__class__.__name__)
#         compact = _compact_snippets(code_snippets)
#         task_input = {"code_snippets": compact}
#         prompt = build_metric_prompt(
#             rubric=self.RUBRIC, metric_id=self.METRIC_ID,
#             input_key_meanings=self.INPUT_MEANINGS, task_input=task_input,
#             example_input=ex["example_input"], example_output=ex["example_output"],
#         )
#         logger.debug(f"[{self.METRIC_ID}] prompt_len={len(prompt)}; n_snippets={len(compact)}")
#         with timed(f"metric.{self.METRIC_ID}"):
#             out = _call_llm_json(self, prompt)
#         out = _finalize_metric(out, self.METRIC_ID)
#         logger.info(f"[{self.METRIC_ID}] band={out['band']} rationale={out['rationale']}")
#         if out["flags"]: logger.info(f"[{self.METRIC_ID}] flags={out['flags']}")
#         if out["gaps"]:  logger.info(f"[{self.METRIC_ID}] gaps={out['gaps']}")
#         return out

# class NestedLoopsAgent(BaseMicroAgent):
#     METRIC_ID = "code.nested_loops_band"
#     RUBRIC = (
#         "Consider existence + depth + hotspots + alternatives.\n"
#         "Band 5: no problematic nesting (depth ≤2) or refactored hotspots;\n"
#         "Band 4: some nesting (depth ≤3) with mitigations and tests;\n"
#         "Band 3: notable nesting (depth 3–4) with partial mitigations;\n"
#         "Band 2: frequent deep nesting (depth ≥4) and limited tests;\n"
#         "Band 1: widespread deep nesting causing performance/complexity risks."
#     )
#     INPUT_MEANINGS = {"code_snippets[]": "Code where loops and nesting depth can be inferred."}

#     def evaluate(self, code_snippets: List[str], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
#         ex = get_one_shot(self.__class__.__name__)
#         compact = _compact_snippets(code_snippets)
#         task_input = {"code_snippets": compact}
#         prompt = build_metric_prompt(
#             rubric=self.RUBRIC, metric_id=self.METRIC_ID,
#             input_key_meanings=self.INPUT_MEANINGS, task_input=task_input,
#             example_input=ex["example_input"], example_output=ex["example_output"],
#         )
#         logger.debug(f"[{self.METRIC_ID}] prompt_len={len(prompt)}; n_snippets={len(compact)}")
#         with timed(f"metric.{self.METRIC_ID}"):
#             out = _call_llm_json(self, prompt)
#         out = _finalize_metric(out, self.METRIC_ID)
#         logger.info(f"[{self.METRIC_ID}] band={out['band']} rationale={out['rationale']}")
#         if out["flags"]: logger.info(f"[{self.METRIC_ID}] flags={out['flags']}")
#         if out["gaps"]:  logger.info(f"[{self.METRIC_ID}] gaps={out['gaps']}")
#         return out