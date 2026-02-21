from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json
import time
from config import WEB_USERNAME, WEB_PASSWORD, LOGIN_SITE, TRAINING_SITE
import re


def parse_rest_time(rest_string):
    """
    Parses string like:
    "90 - 120 sek." -> (90, 120)
    "120 sek."      -> (120, 120)

    Returns: (min_seconds, max_seconds) or (None, None)
    """
    if not rest_string or rest_string == "?":
        return (None, None)

    rest_string = rest_string.replace("sek.", "").replace("sek", "").strip()

    if "-" in rest_string:
        parts = rest_string.split("-")
        try:
            return int(parts[0].strip()), int(parts[1].strip())
        except:
            return (None, None)
    else:
        try:
            val = int(rest_string.strip())
            return (val, val)
        except:
            return (None, None)


def scrape_training_plan(email, password):
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  #uncomment to run without window

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    wait = WebDriverWait(driver, 15)

    try:
        print("Logging in...")
        driver.get(LOGIN_SITE)

        wait.until(EC.presence_of_element_located((By.NAME, "email")))

        driver.find_element(By.NAME, "email").send_keys(email)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.CLASS_NAME, "submit").click()

        time.sleep(3)

        print("Gathering exercise plan...")
        driver.get(TRAINING_SITE)

        wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "ul.skewed-menu > li.skewed-menu__item")
            )
        )

        day_items = driver.find_elements(
            By.CSS_SELECTOR, "ul.skewed-menu > li.skewed-menu__item"
        )

        print(f"Found {len(day_items)} days")

        all_exercises = {}

        for i in range(len(day_items)):
            day_items = driver.find_elements(
                By.CSS_SELECTOR, "ul.skewed-menu > li.skewed-menu__item"
            )
            item = day_items[i]

            subtitle = (
                item.find_element(By.CLASS_NAME, "skewed-menu__subtitle")
                .text.strip()
                .lower()
            )

            if subtitle in ["odpoczynek", "aktywny"]:
                print(f"Day {i+1}: {subtitle.upper()} (skipping)")
                continue

            print(f"Day {i+1}: WORKOUT - processing...")

            button = item.find_element(By.TAG_NAME, "button")
            driver.execute_script("arguments[0].click();", button)

            # wait to load more than one training cards
            wait.until(
                lambda d: len(d.find_elements(
                    By.CSS_SELECTOR, "div[class*='exerciseCard']")
                ) >= 1
            )

            # optional scroll for React lazy-load
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.5)

            cards = driver.find_elements(
                By.CSS_SELECTOR,
                "div[class*='exerciseCard'], div[class*='restCard']"
            )

            print(f"  Found {len(cards)} excercise cards")

            day_exercises = []
            last_exercise = None

            for card in cards:

                class_attr = card.get_attribute("class")

                # ==========================
                # IF EXERCISE
                # ==========================
                if "exerciseCard" in class_attr:
                    try:
                        title_elem = card.find_element(By.CSS_SELECTOR, "div[class*='title']")
                        lines = title_elem.text.split("\n")
                        exercise_name = lines[-1].strip()

                        warm_up_sets = None
                        working_sets = None

                        # warmup sets
                        try:
                            warmup_elem = card.find_element(By.CSS_SELECTOR, "div.warmUpSeriesWrapper--UUKgX > div.series--3JLlw")
                            warm_up_sets = int(warmup_elem.text.strip())
                        except:
                            warm_up_sets = None

                        # working sets
                        try:
                            working_elem = card.find_element(By.CSS_SELECTOR, "div.seriesWrapper--mb7h4:not(.warmUpSeriesWrapper--UUKgX) > div.series--3JLlw")
                            working_sets = int(working_elem.text.strip())
                        except:
                            working_sets = None

                        # reps
                        reps = []
                        repeat_elems = card.find_elements(By.CSS_SELECTOR, "li[class*='repeat']")
                        for rep in repeat_elems:
                            txt = rep.text.strip()
                            try:
                                reps.append(int(txt))
                            except:
                                reps.append(txt)

                        # rest between sets
                        try:
                            rest_elem = card.find_element(By.CSS_SELECTOR, "div[class*='seriesPause']")
                            rest_between_sets = rest_elem.text.strip()
                        except:
                            rest_between_sets = "?"

                        rest_min, rest_max = parse_rest_time(rest_between_sets)

                        exercise_data = {
                            #"type": "exercise",
                            "exercise": exercise_name,
                            "warm_up_sets": warm_up_sets,
                            "working_sets": working_sets,
                            "reps": reps,
                            "rest_between_sets": rest_between_sets,
                            "rest_between_sets_min": rest_min,
                            "rest_between_sets_max": rest_max,
                            "rest_after_exercise_min": None,
                            "rest_after_exercise_max": None
                        }

                        day_exercises.append(exercise_data)
                        last_exercise = exercise_data

                    except Exception as e:
                        print("Exercise error:", e)

                # ==========================
                # IF REST BETWEEN EXERCISES
                # ==========================
                elif "restCard" in class_attr:
                    if not last_exercise:
                        print("Warning: rest card without previous exercise")
                        continue

                    try:
                        card_texts = [el.text.strip() for el in card.find_elements(By.XPATH, ".//*") if el.text.strip()]

                        rest_text = None
                        for txt in card_texts:
                            if re.search(r"\d+\s*-\s*\d+|\d+", txt):
                                rest_text = txt
                                break

                        if rest_text:
                            rest_min, rest_max = parse_rest_time(rest_text)
                        else:
                            rest_min, rest_max = None, None

                        last_exercise["rest_after_exercise_min"] = rest_min
                        last_exercise["rest_after_exercise_max"] = rest_max

                    except Exception as e:
                        print("Error processing rest card:", e)

            '''day_exercises = [
                ex for ex in day_exercises if ex["type"] == "exercise"
            ]'''

            print(f"  Saved {len(day_exercises)} exercises")

            all_exercises[f"Day {i+1}"] = day_exercises

        return all_exercises

    finally:
        driver.quit()

if __name__ == "__main__":

    training_plan = scrape_training_plan(
        WEB_USERNAME, WEB_PASSWORD
    )

    with open("training_plan.json", "w", encoding="utf-8") as f:
        json.dump(training_plan, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 80)
    print("Plan saved to: training_plan.json")
    print("=" * 80)