import json
from config import WEB_USERNAME, WEB_PASSWORD, JSON_PATH
from extract import scrape_training_plan
from utils import log

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
