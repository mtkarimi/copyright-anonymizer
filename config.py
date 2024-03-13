import re
import logging
from typing import List, Dict, Any

from pydantic import BaseModel

# Setup basic configuration for logging in config module, if not already configured in the main module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EntityTypes(BaseModel):
    PEOPLE: str = "people"
    COMPANIES: str = "companies"

# Configuration constants
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200
CHECKPOINT_PATH = 'checkpoint.json'
OUTPUT_FILE_PATH = 'modified_text.txt'  # Added constant for the default output file path

def replace_directly(text: str, replacements: List[Dict[str, str]]) -> str:
    for replacement in replacements:
        text = text.replace(replacement["old"], replacement["new"])
    return text



def replace_with_regex(text: str, replacements: List[Dict[str, str]]) -> str:
    for replacement in replacements:
        pattern = replacement["pattern"]
        repl = replacement["replacement"]
        text = re.sub(pattern, repl, text, flags=re.IGNORECASE)
    return text

def apply_replacements(text: str, config: Dict[str, Any]) -> str:
    if "direct" in config:
        text = replace_directly(text, config["direct"])
    if "regex" in config:
        text = replace_with_regex(text, config["regex"])
    return text

REPLACEMENTS_CONFIG = {}

# REPLACEMENTS_CONFIG = {
#     "direct": [
#         {"old": "XXXX", "new": "YYYY"},
#         {"old": "CompanyName", "new": "[Anonymized Company]"},
#         # Add more direct replacements here
#     ],
#     "regex": [
#         {"pattern": r"\bScalable\b(?=\W|$)", "replacement": "Sultan is here"},
#         {"pattern": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "replacement": "[Anonymized Email]"},
#         # Add more regex replacements here
#     ]
# }
