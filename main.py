import json
from datetime import date
from config import WEB_USERNAME, WEB_PASSWORD, JSON_PATH
from src.extract import scrape_training_plan
from src.utils import log
from src.load import save_to_database

if __name__ == "__main__":

    log("=" * 80)
    log("SCRAPING PROCESS STARTED")
    log("=" * 80)

    training_plan = scrape_training_plan(
        WEB_USERNAME, WEB_PASSWORD
    )

    log("Saving results to JSON")

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(training_plan, f, ensure_ascii=False, indent=2)

    log(f"Plan saved to: {JSON_PATH}")

    log("=" * 80)
    log("SCRAPING PROCESS ENDED")
    log("=" * 80)
    
    log("=" * 80)
    log("LOADING PROCESS STARTED")
    log("=" * 80)

    save_to_database(json_file=JSON_PATH, plan_name="Luty 2025", start_date=date(2025, 2, 1))

    log("=" * 80)
    log("LOADING PROCESS ENDED")
    log("=" * 80)
