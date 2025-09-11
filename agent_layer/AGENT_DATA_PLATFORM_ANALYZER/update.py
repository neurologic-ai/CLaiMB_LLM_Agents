import os
import json
from typing import Dict, List, Any
from agent_layer.AGENT_DATA_PLATFORM_ANALYZER.map_dp import AimriData
from dotenv import load_dotenv
import openai
from concurrent.futures import ThreadPoolExecutor, as_completed
from loguru import logger

# Configure loguru logger
LOG_DIR = "logs/AGENT_DATA_PLATFORM_ANALYZER"
os.makedirs(LOG_DIR, exist_ok=True)
logger.add(f"{LOG_DIR}/data_platform_analyzer.log", rotation="10 MB", retention="10 days", level="INFO")

# Load environment variables from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def _ask_openai(prompt: str, model: str = "gpt-4") -> Any:
    """Helper: call OpenAI chat model and return parsed JSON or raw response content."""
    try:
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a structured evaluator. Always return valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
        )
        
        raw = response.choices[0].message.content.strip()
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return raw
    except Exception as e:
        logger.error(f"_ask_openai error: {str(e)}")
        return []

def elaborate(metric_name: str) -> str:
    prompt = (
        f"Elaborate on the following data pipeline evaluation metric: '{metric_name}'. "
        f"Provide a detailed description of what it means and why it's important."
    )
    
    description = _ask_openai(prompt)
    
    if isinstance(description, dict):
        return json.dumps(description, indent=2)
    return description

def process_metric(metric: str, aimri_points: List[Dict[str, str]]) -> (str, List[Dict[str, str]]):
    logger.info(f"Processing metric: {metric}")

    description = elaborate(metric)
    logger.debug(f"Elaboration for '{metric}': {description}")

    aimri_list_text = "\n".join(
        [f"{point['id']} - {point['category']}: {point['name']}" for point in aimri_points]
    )

    prompt = (
        f"You are an expert in MLOps and AI metrics evaluation. "
        f"The following is a detailed description of a metric:\n\n"
        f"\"\"\"\n{description}\n\"\"\"\n\n"
        f"The AIMRI consists of the following points:\n{aimri_list_text}\n\n"
        f"Based on the description, select the most relevant 3 AIMRI points. "
        f"For each relevant point, respond with its ID only as a JSON array (e.g., [\"1.2\", \"2.4\"]). "
        f"If none are relevant, respond with an empty list []."
    )

    matched_ids = _ask_openai(prompt)

    if not isinstance(matched_ids, list):
        logger.warning(f"Unexpected _ask_openai output for '{metric}', using empty list. RAW: {matched_ids}")
        matched_ids = []

    matched_points = [
        {
            "dimension": f"{point['id'].split('.')[0].zfill(2)}. {point['category']}",
            "subsection": f"{point['id']} {point['name']}"
        }
        for point in aimri_points
        if point['id'] in matched_ids
    ]

    logger.info(f"Mapped {metric} to AIMRI points: {matched_ids}")
    return metric, matched_points

def map_metrics_to_aimri() -> Dict[str, List[Dict[str, str]]]:
    logger.info("Starting mapping of evaluation metrics to AIMRI points.")

    data = AimriData()
    aimri_points = data.get_aimri_points()
    evaluation_metrics = data.get_evaluation_metrics()

    mapping: Dict[str, List[Dict[str, str]]] = {}

    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_metric = {
            executor.submit(process_metric, metric, aimri_points): metric
            for metric in evaluation_metrics
        }

        for future in as_completed(future_to_metric):
            try:
                metric_name, matched_points = future.result()
                mapping[metric_name] = matched_points
            except Exception as e:
                logger.error(f"Error processing metric: {str(e)}")

    logger.info("Completed mapping all metrics.")
    return mapping

def save_mapping_to_file(mapping: Dict[str, List[Dict[str, str]]]) -> None:
    file_path = r'agent_layer\AGENT_DATA_PLATFORM_ANALYZER\aimri_mapping.py'
    with open(file_path, 'w') as f:
        f.write("from typing import Dict, List\n\n")
        f.write("MLOPS_METRIC_TO_AIMRI: Dict[str, List[Dict[str, str]]] = ")
        json.dump(mapping, f, indent=4)
    logger.info(f"Saved mapping to '{file_path}'.")

if __name__ == "__main__":
    mapping = map_metrics_to_aimri()
    save_mapping_to_file(mapping)
    logger.info("All done.")
