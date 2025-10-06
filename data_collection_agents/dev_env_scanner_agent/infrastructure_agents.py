# from __future__ import annotations
# from typing import Any, Dict, List, Optional
# from loguru import logger

# from data_collection_agents.dev_env_scanner_agent.base_agent import BaseMicroAgent
# from data_collection_agents.dev_env_scanner_agent.one_shot.registry import get_one_shot
# from data_collection_agents.dev_env_scanner_agent.one_shot.utils import build_one_shot_prompt
# from data_collection_agents.dev_env_scanner_agent.logging_utils import timed

# _JSON_ONLY = "Return ONLY a single JSON object. No prose."

# class CICDAgent(BaseMicroAgent):
#     def evaluate(self, file_paths: List[str], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
#         ex = get_one_shot(self.__class__.__name__)
#         prompt = build_one_shot_prompt(
#             system_preamble="You are a CI/CD analyst.",
#             response_format_description=(
#                 '{"ci_files": {"github_actions": <int>, "gitlab_ci": <int>, "jenkins": <int>}, '
#                 '"ci_workflow_count": <int>, "ci_quality": <0-1>, "deployment_automation": <0-1>}'
#             ),
#             task_input={"file_paths": file_paths},
#             input_key_meanings=ex.get("input_key_meanings", {}),
#             example_input=ex["example_input"],
#             example_output=ex["example_output"],
#         )
#         with timed("metric.cicd"):
#             out = self._parse_json_response(self._call_llm(prompt, _JSON_ONLY)) or {}
#         ci = out.get("ci_files", {}) or {}
#         count = int(out.get("ci_workflow_count", 0))
#         has_github = ci.get("github_actions", 0) > 0 or ci.get("github", 0) > 0
#         has_gitlab = ci.get("gitlab_ci", 0) > 0 or ci.get("gitlab", 0) > 0
#         has_jenkins = ci.get("jenkins", 0) > 0
#         return {
#             "ci_workflow_count": count,
#             "has_ci": count > 0 or has_github or has_gitlab or has_jenkins,
#             "ci_quality": float(out.get("ci_quality", 0.0)),
#             "deployment_automation": float(out.get("deployment_automation", 0.0)),
#             "has_github_actions": bool(has_github),
#             "has_gitlab_ci": bool(has_gitlab),
#             "has_jenkins": bool(has_jenkins),
#         }

# class DeploymentAgent(BaseMicroAgent):
#     def evaluate(self, file_paths: List[str], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
#         ex = get_one_shot(self.__class__.__name__)
#         prompt = build_one_shot_prompt(
#             system_preamble="You are a deployment analyst.",
#             response_format_description=(
#                 '{"deployment_files": {"docker": <int>, "kubernetes": <int>, "helm": <int>}, '
#                 '"deploy_script_count": <int>, "deployment_automation": <0-1>, "deployment_quality": <0-1>}'
#             ),
#             task_input={"file_paths": file_paths},
#             input_key_meanings=ex.get("input_key_meanings", {}),
#             example_input=ex["example_input"],
#             example_output=ex["example_output"],
#         )
#         with timed("metric.deployment"):
#             out = self._parse_json_response(self._call_llm(prompt, _JSON_ONLY)) or {}
#         count = int(out.get("deploy_script_count", 0))
#         out2: Dict[str, Any] = {
#             "deploy_script_count": count,
#             "has_deploy_scripts": count > 0,
#             "deployment_automation": float(out.get("deployment_automation", 0.0)),
#             "deployment_quality": float(out.get("deployment_quality", 0.0)),
#         }
#         for dtype, dcount in (out.get("deployment_files", {}) or {}).items():
#             out2[f"has_{str(dtype).strip().lower()}"] = bool(dcount)
#         return out2

# class EnvironmentConfigAgent(BaseMicroAgent):
#     _CANON = {
#         "requirements.txt": "has_requirements",
#         "requirements": "has_requirements",
#         "pipfile": "has_pipfile",
#         "environment.yml": "has_env_yml",
#         "environment.yaml": "has_env_yml",
#         "conda.yml": "has_env_yml",
#         "pyproject.toml": "has_pyproject_toml",
#         "setup.py": "has_setup_py",
#     }
#     def evaluate(self, file_paths: List[str], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
#         ex = get_one_shot(self.__class__.__name__)
#         prompt = build_one_shot_prompt(
#             system_preamble="You are a dependency management analyst.",
#             response_format_description=(
#                 '{"dependency_files": {"requirements.txt": <true|false>, "pyproject.toml": <true|false>}, '
#                 '"dependency_management_quality": <0-1>, "environment_consistency": <0-1>, '
#                 '"best_practices": ["<string>", "..."]}'
#             ),
#             task_input={"file_paths": file_paths},
#             input_key_meanings=ex.get("input_key_meanings", {}),
#             example_input=ex["example_input"],
#             example_output=ex["example_output"],
#         )
#         with timed("metric.env_config"):
#             out = self._parse_json_response(self._call_llm(prompt, _JSON_ONLY)) or {}
#         raw = out.get("dependency_files", {}) or {}
#         res: Dict[str, Any] = {v: False for v in self._CANON.values()}
#         for k, present in raw.items():
#             canon = self._CANON.get(str(k).strip().lower())
#             if canon:
#                 res[canon] = bool(present)
#         res.setdefault("has_requirements", False)
#         res.setdefault("has_pipfile", False)
#         res.setdefault("has_env_yml", False)
#         res["dependency_management_quality"] = float(out.get("dependency_management_quality", 0.0))
#         res["environment_consistency"] = float(out.get("environment_consistency", 0.0))
#         res["dependency_best_practices"] = out.get("best_practices", [])
#         return res

# class ExperimentDetectionAgent(BaseMicroAgent):
#     def evaluate(self, file_paths: List[str], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
#         ex = get_one_shot(self.__class__.__name__)
#         prompt = build_one_shot_prompt(
#             system_preamble="You are an experiment management analyst.",
#             response_format_description=(
#                 '{"experiment_dirs": ["<dir>", "..."], "experiment_folder_count": <int>, '
#                 '"experiment_management": <0-1>, "reproducibility_analysis": ["<string>", "..."]}'
#             ),
#             task_input={"file_paths": file_paths},
#             input_key_meanings=ex.get("input_key_meanings", {}),
#             example_input=ex["example_input"],
#             example_output=ex["example_output"],
#         )
#         with timed("metric.experiments"):
#             out = self._parse_json_response(self._call_llm(prompt, _JSON_ONLY)) or {}
#         cnt = int(out.get("experiment_folder_count", 0))
#         return {
#             "experiment_folder_count": cnt,
#             "has_experiments": cnt > 0,
#             "experiment_dirs": out.get("experiment_dirs", []),
#             "experiment_management": float(out.get("experiment_management", 0.0)),
#             "reproducibility_analysis": out.get("reproducibility_analysis", []),
#         }

# class ProjectStructureAgent(BaseMicroAgent):
#     def evaluate(self, file_paths: List[str], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
#         ex = get_one_shot(self.__class__.__name__)
#         prompt = build_one_shot_prompt(
#             system_preamble="You are a project structure analyst.",
#             response_format_description=(
#                 '{"structure_quality": <0-1>, "organization_patterns": ["<string>", "..."], '
#                 '"documentation_quality": <0-1>, "best_practices_adherence": <0-1>}'
#             ),
#             task_input={"file_paths": file_paths},
#             input_key_meanings=ex.get("input_key_meanings", {}),
#             example_input=ex["example_input"],
#             example_output=ex["example_output"],
#         )
#         with timed("metric.project_structure"):
#             out = self._parse_json_response(self._call_llm(prompt, _JSON_ONLY)) or {}
#         return {
#             "structure_quality": float(out.get("structure_quality", 0.0)),
#             "organization_patterns": out.get("organization_patterns", []),
#             "documentation_quality": float(out.get("documentation_quality", 0.0)),
#             "best_practices_adherence": float(out.get("best_practices_adherence", 0.0)),
#         }