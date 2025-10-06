# data_collection_agents/dev_env_scanner_agent/utils/text.py
from typing import List

def label_snippets(snippets: List[str]) -> List[str]:
    """Prefix each snippet with a header, but return a LIST to keep model context sane."""
    out = []
    for i, s in enumerate(snippets, 1):
        out.append(f"--- Snippet {i} ---\n{s}")
    return out