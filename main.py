import json
from datetime import date
from config import WEB_USERNAME, WEB_PASSWORD, JSON_PATH, WORKOUT_XLSX_PATH
from src.extract import scrape_training_plan
from src.utils import log, clear_screen
from src.ui import plan_selector, workout_day_selector_export, workout_day_selector_import
from src.load import save_plan_to_database, save_workout_to_database
from src.genxlsx import generate_workout_excel


if __name__ == "__main__":

    today = date.today()
    
    while True:
        
        clear_screen()
        print("1. Gather this months training plan and import it to DB")
        print("2. Generate workout excel file")
        print("3. Import workout day to DB")
        print("0. Quit")
        choice = input("\nEnter choice: ").strip()

        match choice:
            case "1":
                
                clear_screen()
                log("=" * 80)
                log("SCRAPING PROCESS STARTED", echo=True)
                log("=" * 80)

                training_plan = scrape_training_plan(
                    WEB_USERNAME, WEB_PASSWORD
                )

                log("Saving results to JSON")

                with open(JSON_PATH, "w", encoding="utf-8") as f:
                    json.dump(training_plan, f, ensure_ascii=False, indent=2)

                log(f"Plan saved to: {JSON_PATH}")

                log("=" * 80)
                log("SCRAPING PROCESS ENDED", echo=True)
                log("=" * 80)
                log("=" * 80)
                log("LOADING PROCESS STARTED", echo=True)
                log("=" * 80)

                save_plan_to_database(json_file=JSON_PATH, plan_name=today.strftime("%B %Y"), start_date=today)

                log("=" * 80)
                log("LOADING PROCESS ENDED", echo=True)
                log("=" * 80)

                print("\n" + "=" * 80)
                print("Data gathered and imported successfuly")
                print("=" * 80 + "\n")
                input("Press Enter to continue...")
            
            case "2":

                result = plan_selector()

                if result is not None:

                    plan_id, plan_name = result
                    day = workout_day_selector_export(plan_id, plan_name)

                    if day is not None:

                        clean_file_name = f"workout_{plan_name}_{day}_{today.strftime('%Y-%m-%d')}.xlsx".replace(" ", "_").lower()
                        output_file = WORKOUT_XLSX_PATH / clean_file_name

                        generate_workout_excel(
                            plan_name=plan_name,
                            day_of_week=day,
                            output_file=output_file
                        )

                        print("\n" + "=" * 80)
                        print("Excel file generated")
                        print("=" * 80 + "\n")
                        input("Press Enter to continue...")

            case "3":
                workout_file = workout_day_selector_import()
                clear_screen()

                if workout_file is not None:
                    print(f"Workout file selected: {workout_file.split("/")[-1]}")
                    response = input("\nImport workout data to DB? [Y/n]:").strip().lower()

                    if response in ["", "y", "yes"]:
                        save_workout_to_database(workout_file)
                    else:
                        print("\nImport canceled")
                        input("Press Enter to continue...")

            case "0":
                break

            case _:
                print("Invalid choice! Please select one of the menu options by number.")
                input("Press Enter to continue...")    
