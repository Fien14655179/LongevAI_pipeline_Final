import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")

# Models
EMBEDDING_MODEL = "emilyalsentzer/Bio_ClinicalBERT"
LLM_PROVIDER = "openrouter"
HF_LLM_MODEL = "longevity-ai-4432/longevity-finetuned-v1"
OPENROUTER_LLM_MODEL = "openai/gpt-oss-120b:free"

# Pipeline settings
TOP_K_ACTIONS = 5  # hoeveel acties per gebruiker

# Taxonomy
CATEGORIES = [
    "Nutrition",
    "Sleep & Recovery",
    "Exercise & Movement",
    "Stress Management",
    "Cognitive Performance",
    "Inflammation",
    "Metabolic Health",
    "Cardiovascular Health",
    "Gut Health",
    "Longevity Protocols"
]

# Paths
DATA_DIR = "data"
ACTIONS_LIBRARY_PATH = "actions_library/actions.json"
OUTPUT_PATH = "output/report.json"