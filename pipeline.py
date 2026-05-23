import asyncio
import json
import os
import logging
from datetime import datetime
from config import DATA_DIR, OUTPUT_PATH
from embeddings import get_top_actions
from llm import generate_report

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def load_profile(filepath):
    with open(filepath, "r") as f:
        return json.load(f)

def parse_llm_output(raw_output):
    clean = raw_output.strip()
    if clean.startswith("```json"):
        clean = clean[7:]
    if clean.startswith("```"):
        clean = clean[3:]
    if clean.endswith("```"):
        clean = clean[:-3]
    return json.loads(clean.strip())

async def process_user(filepath):
    filename = os.path.basename(filepath)
    try:
        logger.info(f"Processing {filename}...")
        
        profile = load_profile(filepath)
        top_actions = get_top_actions(profile)
        raw_output = generate_report(profile, top_actions)
        blueprint = parse_llm_output(raw_output)
        
        logger.info(f"Successfully processed {filename}")
        return {
            "user_id": profile["user_id"],
            "name": profile["name"],
            "status": "success",
            "blueprint": blueprint
        }

    except Exception as e:
        logger.error(f"Failed to process {filename}: {str(e)}")
        return {
            "user_id": filename,
            "status": "failure",
            "error": str(e)
        }

async def run_pipeline():
    files = [
        os.path.join(DATA_DIR, f)
        for f in os.listdir(DATA_DIR)
        if f.endswith(".json")
    ]

    logger.info(f"Starting pipeline for {len(files)} profiles...")

    tasks = [process_user(f) for f in files]
    results = await asyncio.gather(*tasks)

    report = {
        "generated_at": datetime.now().isoformat(),
        "total_processed": len(results),
        "successful": sum(1 for r in results if r["status"] == "success"),
        "failed": sum(1 for r in results if r["status"] == "failure"),
        "results": results
    }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(report, f, indent=2)

    logger.info(f"Pipeline complete! Report saved to {OUTPUT_PATH}")
    logger.info(f"Successful: {report['successful']}/{report['total_processed']}")

if __name__ == "__main__":
    asyncio.run(run_pipeline())