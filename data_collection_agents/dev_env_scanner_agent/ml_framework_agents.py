# from __future__ import annotations
# from typing import Any, Dict, List, Optional
# from data_collection_agents.dev_env_scanner_agent.base_agent import BaseMicroAgent
# from data_collection_agents.dev_env_scanner_agent.one_shot.registry import get_one_shot
# from data_collection_agents.dev_env_scanner_agent.one_shot.prompting import build_metric_prompt
# from data_collection_agents.dev_env_scanner_agent.logging_utils import timed

# def _join_snippets(snippets: List[str]) -> str:
#     return "\n\n".join(f"--- Snippet {i} ---\n{s}" for i, s in enumerate(snippets, 1))

# def _band(v: Any) -> int:
#     try:
#         x = int(v);  return 1 if x < 1 else 5 if x > 5 else x
#     except Exception:
#         return 3

# class DataValidationAgent(BaseMicroAgent):
#     METRIC_ID = "ml.data_validation"
#     RUBRIC = (
#         "Assess schema/value/drift checks and CI gating.\n"
#         "5: strong rules + drift + CI gates; 4: solid checks; 3: some checks; 2: ad-hoc; 1: none."
#     )
#     INPUT_MEANINGS = {"code_snippets[]": "Pipelines validating schemas/distributions/drift."}
#     def evaluate(self, code_snippets: List[str], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
#         ex = get_one_shot(self.__class__.__name__)
#         ti = {"code_snippets": _join_snippets(code_snippets)}
#         p = build_metric_prompt(rubric=self.RUBRIC, metric_id=self.METRIC_ID,
#                                 input_key_meanings=self.INPUT_MEANINGS, task_input=ti,
#                                 example_input=ex["example_input"], example_output=ex["example_output"])
#         with timed("metric.ml.data_validation"):
#             out = self._parse_json_response(self._call_llm(p, "")) or {}
#         return {
#             "metric_id": self.METRIC_ID,
#             "band": _band(out.get("band", 3)),
#             "rationale": out.get("rationale", "No rationale."),
#             "flags": out.get("flags", []),
#             "gaps": out.get("gaps", []),
#         }

# class ExperimentTrackingAgent(BaseMicroAgent):
#     METRIC_ID = "ml.experiment_tracking"
#     RUBRIC = "Params/metrics/artifacts/signature/lineage across runs."
#     INPUT_MEANINGS = {"code_snippets[]": "Training code that logs with MLflow/W&B/ClearML."}
#     def evaluate(self, code_snippets: List[str], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
#         ex = get_one_shot(self.__class__.__name__)
#         ti = {"code_snippets": _join_snippets(code_snippets)}
#         p = build_metric_prompt(rubric=self.RUBRIC, metric_id=self.METRIC_ID,
#                                 input_key_meanings=self.INPUT_MEANINGS, task_input=ti,
#                                 example_input=ex["example_input"], example_output=ex["example_output"])
#         with timed("metric.ml.exp_tracking"):
#             out = self._parse_json_response(self._call_llm(p, "")) or {}
#         return {"metric_id": self.METRIC_ID, "band": _band(out.get("band", 3)),
#                 "rationale": out.get("rationale", "No rationale."), "flags": out.get("flags", []), "gaps": out.get("gaps", [])}

# class HyperparameterOptimizationAgent(BaseMicroAgent):
#     METRIC_ID = "ml.hpo_practice"
#     RUBRIC = "Search strategy, seeds, persistence; 5→1 from rigorous→none."
#     INPUT_MEANINGS = {"code_snippets[]": "HPO code/configs"}
#     def evaluate(self, code_snippets: List[str], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
#         ex = get_one_shot(self.__class__.__name__)
#         ti = {"code_snippets": _join_snippets(code_snippets)}
#         p = build_metric_prompt(rubric=self.RUBRIC, metric_id=self.METRIC_ID,
#                                 input_key_meanings=self.INPUT_MEANINGS, task_input=ti,
#                                 example_input=ex["example_input"], example_output=ex["example_output"])
#         with timed("metric.ml.hpo"):
#             out = self._parse_json_response(self._call_llm(p, "")) or {}
#         return {"metric_id": self.METRIC_ID, "band": _band(out.get("band", 3)),
#                 "rationale": out.get("rationale", "No rationale."), "flags": out.get("flags", []), "gaps": out.get("gaps", [])}

# class MLFrameworkAgent(BaseMicroAgent):
#     METRIC_ID = "ml.framework_maturity"
#     RUBRIC = "Clarity/consistency of primary framework; idioms; interop."
#     INPUT_MEANINGS = {"code_snippets[]": "Training/inference code to infer framework usage"}
#     def evaluate(self, code_snippets: List[str], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
#         ex = get_one_shot(self.__class__.__name__)
#         ti = {"code_snippets": _join_snippets(code_snippets)}
#         p = build_metric_prompt(rubric=self.RUBRIC, metric_id=self.METRIC_ID,
#                                 input_key_meanings=self.INPUT_MEANINGS, task_input=ti,
#                                 example_input=ex["example_input"], example_output=ex["example_output"])
#         with timed("metric.ml.framework"):
#             out = self._parse_json_response(self._call_llm(p, "")) or {}
#         return {"metric_id": self.METRIC_ID, "band": _band(out.get("band", 3)),
#                 "rationale": out.get("rationale", "No rationale."), "flags": out.get("flags", []), "gaps": out.get("gaps", [])}

# class ModelEvaluationAgent(BaseMicroAgent):
#     METRIC_ID = "ml.evaluation_practice"
#     RUBRIC = "Metrics breadth, calibration/fairness, reporting."
#     INPUT_MEANINGS = {"code_snippets[]": "Evaluation scripts and metrics usage"}
#     def evaluate(self, code_snippets: List[str], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
#         ex = get_one_shot(self.__class__.__name__)
#         ti = {"code_snippets": _join_snippets(code_snippets)}
#         p = build_metric_prompt(rubric=self.RUBRIC, metric_id=self.METRIC_ID,
#                                 input_key_meanings=self.INPUT_MEANINGS, task_input=ti,
#                                 example_input=ex["example_input"], example_output=ex["example_output"])
#         with timed("metric.ml.eval"):
#             out = self._parse_json_response(self._call_llm(p, "")) or {}
#         return {"metric_id": self.METRIC_ID, "band": _band(out.get("band", 3)),
#                 "rationale": out.get("rationale", "No rationale."), "flags": out.get("flags", []), "gaps": out.get("gaps", [])}

# class ModelTrainingAgent(BaseMicroAgent):
#     METRIC_ID = "ml.training_practice"
#     RUBRIC = "Entrypoints/configs/seeds/checkpoints/recovery."
#     INPUT_MEANINGS = {"code_snippets[]": "Entrypoints starting training"}
#     def evaluate(self, code_snippets: List[str], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
#         ex = get_one_shot(self.__class__.__name__)
#         ti = {"code_snippets": _join_snippets(code_snippets)}
#         p = build_metric_prompt(rubric=self.RUBRIC, metric_id=self.METRIC_ID,
#                                 input_key_meanings=self.INPUT_MEANINGS, task_input=ti,
#                                 example_input=ex["example_input"], example_output=ex["example_output"])
#         with timed("metric.ml.train"):
#             out = self._parse_json_response(self._call_llm(p, "")) or {}
#         return {"metric_id": self.METRIC_ID, "band": _band(out.get("band", 3)),
#                 "rationale": out.get("rationale", "No rationale."), "flags": out.get("flags", []), "gaps": out.get("gaps", [])}